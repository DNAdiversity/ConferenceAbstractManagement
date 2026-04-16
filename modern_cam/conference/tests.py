from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.test.utils import override_settings

from .models import (
    Author,
    ProgramSession,
    ProgramSlot,
    ReviewAssignment,
    ReviewerTopicExpertise,
    Submission,
    SubmissionNotification,
    SubmissionSnapshot,
    Topic,
)
from .roles import ensure_role_groups


class SubmissionFlowTests(TestCase):
    def setUp(self):
        ensure_role_groups()
        self.user = User.objects.create_user(username="submitter@example.com", email="submitter@example.com", password="strong-password")
        self.topic = Topic.objects.create(category="Genomics", name="Environmental DNA")

    def submission_payload(self, **overrides):
        payload = {
            "title": "Modern DNA barcoding workflows",
            "presentation_type": Submission.PresentationType.TALK,
            "abstract_text": "A secure rebuild of the conference system.",
            "topics": [self.topic.pk],
            "authors-TOTAL_FORMS": 1,
            "authors-INITIAL_FORMS": 0,
            "authors-MIN_NUM_FORMS": 1,
            "authors-MAX_NUM_FORMS": 1000,
            "authors-0-order": 1,
            "authors-0-first_name": "Taylor",
            "authors-0-middle_initial": "",
            "authors-0-last_name": "Rao",
            "authors-0-email": "taylor@example.com",
            "authors-0-institution": "Conference Lab",
            "authors-0-department": "",
            "authors-0-address": "",
            "authors-0-country": "Canada",
            "authors-0-corresponding": "on",
            "authors-0-presenting": "on",
        }
        payload.update(overrides)
        return payload

    def test_submitter_can_create_draft_submission(self):
        client = Client()
        client.login(username="submitter@example.com", password="strong-password")
        response = client.post(
            reverse("submission-create"),
            self.submission_payload(save_draft="1"),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Submission.objects.count(), 1)
        submission = Submission.objects.get()
        self.assertEqual(submission.status, Submission.Status.DRAFT)
        self.assertEqual(submission.authors.count(), 1)
        self.assertTrue(
            submission.snapshots.filter(event_type=SubmissionSnapshot.EventType.DRAFT_SAVED).exists()
        )

    def test_submitter_can_submit_with_receipt_and_snapshot(self):
        client = Client()
        client.login(username="submitter@example.com", password="strong-password")
        response = client.post(
            reverse("submission-create"),
            self.submission_payload(
                certify_authors_approved="on",
                submit_submission="1",
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        submission = Submission.objects.get()
        self.assertEqual(submission.status, Submission.Status.SUBMITTED)
        self.assertTrue(submission.submitter_certified_authors_approved)
        self.assertTrue(
            submission.snapshots.filter(event_type=SubmissionSnapshot.EventType.SUBMITTED).exists()
        )
        self.assertEqual(
            submission.notifications.filter(kind=SubmissionNotification.Kind.SUBMISSION_RECEIPT).count(),
            1,
        )
        self.assertEqual(len(mail.outbox), 1)

    def test_submit_requires_author_certification(self):
        client = Client()
        client.login(username="submitter@example.com", password="strong-password")
        response = client.post(
            reverse("submission-create"),
            self.submission_payload(submit_submission="1"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please confirm that every listed author approved this abstract")
        self.assertEqual(Submission.objects.count(), 0)

    @override_settings(SUBMISSION_DEADLINE=timezone.now() - timedelta(hours=1))
    def test_closed_deadline_blocks_submit(self):
        client = Client()
        client.login(username="submitter@example.com", password="strong-password")
        response = client.post(
            reverse("submission-create"),
            self.submission_payload(
                certify_authors_approved="on",
                submit_submission="1",
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The abstract deadline closed on")
        self.assertEqual(Submission.objects.count(), 0)

    @override_settings(SUBMISSION_DEADLINE=timezone.now() - timedelta(hours=1))
    def test_closed_deadline_still_allows_draft_save(self):
        client = Client()
        client.login(username="submitter@example.com", password="strong-password")
        response = client.post(
            reverse("submission-create"),
            self.submission_payload(save_draft="1"),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        submission = Submission.objects.get()
        self.assertEqual(submission.status, Submission.Status.DRAFT)

    def test_submitter_can_register_with_streamlined_form(self):
        response = self.client.post(
            reverse("register"),
            {
                "email": "newsubmitter@example.org",
                "first_name": "New",
                "last_name": "Submitter",
                "institution": "Conference Lab",
                "country": "Canada",
                "password1": "strong-password-123",
                "password2": "strong-password-123",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email="newsubmitter@example.org")
        self.assertEqual(user.profile.institution, "Conference Lab")
        self.assertEqual(user.profile.country, "Canada")


class PublicTokenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="submitter@example.com", email="submitter@example.com", password="strong-password")
        self.submission = Submission.objects.create(
            submitter=self.user,
            title="Poster proof",
            presentation_type=Submission.PresentationType.POSTER,
            abstract_text="Token test",
            status=Submission.Status.SUBMITTED,
        )
        self.author = Author.objects.create(submission=self.submission, order=1, first_name="Ana", last_name="Lee", email="ana@example.com")

    def test_presenter_token_resolves(self):
        token = self.submission.build_action_token("presenter")
        response = self.client.get(reverse("public-presenter", args=[token]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Poster proof")


class SubmissionReceiptTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="submitter@example.com",
            email="submitter@example.com",
            password="strong-password",
        )
        self.submission = Submission.objects.create(
            submitter=self.user,
            title="Receipt ready abstract",
            presentation_type=Submission.PresentationType.POSTER,
            abstract_text="Receipt test body",
            status=Submission.Status.SUBMITTED,
            submitted_at=timezone.now(),
            submitter_certified_authors_approved=True,
            submitter_certified_authors_approved_at=timezone.now(),
        )
        self.author = Author.objects.create(
            submission=self.submission,
            order=1,
            first_name="Ana",
            last_name="Lee",
            email="ana@example.com",
        )
        self.submission.create_snapshot(
            SubmissionSnapshot.EventType.SUBMITTED,
            actor=self.user,
            note="Submitted for review",
        )
        SubmissionNotification.objects.create(
            submission=self.submission,
            kind=SubmissionNotification.Kind.SUBMISSION_RECEIPT,
            recipient=self.user.email,
            subject=f"Submission receipt: {self.submission.reference_code}",
            sent_by=self.user,
        )
        self.client.login(username="submitter@example.com", password="strong-password")

    def test_submitter_can_open_receipt_page(self):
        response = self.client.get(reverse("submission-receipt", args=[self.submission.public_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.submission.reference_code)
        self.assertContains(response, "Receipt ready abstract")

    def test_submitter_can_resend_receipt(self):
        response = self.client.post(
            reverse("submission-resend-receipt", args=[self.submission.public_id]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            self.submission.notifications.filter(kind=SubmissionNotification.Kind.SUBMISSION_RECEIPT).count(),
            2,
        )
        self.assertTrue(
            self.submission.snapshots.filter(event_type=SubmissionSnapshot.EventType.RECEIPT_RESENT).exists()
        )


class AdminConsoleTests(TestCase):
    def setUp(self):
        ensure_role_groups()
        self.admin_user = User.objects.create_superuser(
            username="admin@example.org",
            email="admin@example.org",
            password="strong-password",
        )
        self.reviewer = User.objects.create_user(
            username="reviewer@example.org",
            email="reviewer@example.org",
            password="strong-password",
            first_name="Riley",
            last_name="Reviewer",
        )
        self.reviewer.groups.add(Group.objects.get(name="Reviewers"))

        self.topic = Topic.objects.create(category="Genomics", name="Metabarcoding")
        self.submission = Submission.objects.create(
            submitter=self.admin_user,
            title="Assignment ready abstract",
            presentation_type=Submission.PresentationType.TALK,
            abstract_text="Abstract ready for admin assignment tools.",
            status=Submission.Status.SUBMITTED,
        )
        self.submission.topics.add(self.topic)
        ReviewerTopicExpertise.objects.create(
            reviewer=self.reviewer,
            topic=self.topic,
            expertise=ReviewerTopicExpertise.Expertise.LEAD,
        )

        self.client = Client()
        self.client.login(username="admin@example.org", password="strong-password")

    def test_admin_console_pages_render(self):
        response = self.client.get(reverse("admin:conference-operations-dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conference operations")

        response = self.client.get(reverse("admin:conference-reviewer-dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reviewer workload and follow-up")

        response = self.client.get(reverse("admin:conference-agenda-dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Review-ready but unscheduled")

    def test_admin_action_auto_assigns_topic_matched_reviewers(self):
        response = self.client.post(
            reverse("admin:conference_submission_changelist"),
            {
                "action": "auto_assign_topic_matched_reviewers",
                "_selected_action": [str(self.submission.pk)],
                "select_across": 0,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        assignment = ReviewAssignment.objects.get(submission=self.submission, reviewer=self.reviewer)
        self.assertIsNotNone(assignment.due_at)
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, Submission.Status.UNDER_REVIEW)

    def test_admin_reviewer_reminder_updates_assignment(self):
        assignment = ReviewAssignment.objects.create(
            submission=self.submission,
            reviewer=self.reviewer,
            assigned_by=self.admin_user,
        )

        response = self.client.post(reverse("admin:conference-reviewer-remind", args=[self.reviewer.pk]), follow=True)
        self.assertEqual(response.status_code, 200)

        assignment.refresh_from_db()
        self.assertEqual(assignment.reminder_count, 1)
        self.assertIsNotNone(assignment.last_reminded_at)
        self.assertEqual(len(mail.outbox), 1)

    def test_admin_agenda_scheduler_creates_slot(self):
        session = ProgramSession.objects.create(
            name="Program Session",
            room="Room A",
            chair_name="Chair",
            starts_at=timezone.now(),
        )

        response = self.client.post(
            reverse("admin:conference-agenda-schedule", args=[self.submission.pk]),
            {
                "session": session.pk,
                "starts_at": "2026-04-15T10:15:00",
                "order": 2,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        slot = ProgramSlot.objects.get(submission=self.submission)
        self.assertEqual(slot.session, session)
        self.assertEqual(slot.order, 2)
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, Submission.Status.SCHEDULED)
