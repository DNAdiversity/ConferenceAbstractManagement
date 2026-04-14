import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core import signing
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Count, Prefetch, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    salutation = models.CharField(max_length=32, blank=True)
    institution = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=128, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=128, blank=True)
    province_state = models.CharField(max_length=128, blank=True)
    postal_code = models.CharField(max_length=32, blank=True)
    reviewer_is_available = models.BooleanField(default=True)
    reviewer_max_assignments = models.PositiveSmallIntegerField(default=6)
    reviewer_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name", "user__email"]

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        full_name = self.user.get_full_name().strip()
        return full_name or self.user.email or self.user.username

    @property
    def reviewer_open_assignments(self):
        return self.user.review_assignments.filter(completed_at__isnull=True).count()


class Topic(TimeStampedModel):
    category = models.CharField(max_length=128)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "name"]
        unique_together = [("category", "name")]

    def __str__(self):
        return f"{self.category}: {self.name}"


class ReviewerTopicExpertise(TimeStampedModel):
    class Expertise(models.TextChoices):
        LEAD = "LEAD", "Lead Reviewer"
        EXPERIENCED = "EXPERIENCED", "Experienced"
        EMERGING = "EMERGING", "Emerging"
        AVOID = "AVOID", "Do Not Assign"

    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topic_expertise")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="reviewer_expertise")
    expertise = models.CharField(max_length=16, choices=Expertise.choices, default=Expertise.EXPERIENCED)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["reviewer__last_name", "reviewer__first_name", "topic__category", "topic__name"]
        unique_together = [("reviewer", "topic")]

    def __str__(self):
        return f"{self.reviewer.get_full_name() or self.reviewer.email} · {self.topic.name}"

    @property
    def expertise_weight(self):
        return {
            self.Expertise.LEAD: 4,
            self.Expertise.EXPERIENCED: 3,
            self.Expertise.EMERGING: 1,
            self.Expertise.AVOID: -99,
        }[self.expertise]


class Submission(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        REVIEWED = "REVIEWED", "Reviewed"
        ASSIGNED_FOR_EDIT = "ASSIGNED_FOR_EDIT", "Assigned For Copy Edit"
        EDITED = "EDITED", "Edited"
        SCHEDULED = "SCHEDULED", "Scheduled"
        FINALIZED = "FINALIZED", "Finalized"

    class PresentationType(models.TextChoices):
        TALK = "TALK", "Talk"
        POSTER = "POSTER", "Poster"
        LIGHTNING = "LIGHTNING", "Lightning Talk"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    title = models.CharField(max_length=300)
    presentation_type = models.CharField(max_length=16, choices=PresentationType.choices)
    abstract_text = models.TextField()
    edited_abstract_text = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    decision_notes = models.TextField(blank=True)
    topics = models.ManyToManyField(Topic, related_name="submissions", blank=True)
    presenter_confirmed_author = models.ForeignKey(
        "Author",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="presenter_confirmations",
    )
    presenter_confirmed_at = models.DateTimeField(null=True, blank=True)
    prize_opt_in = models.BooleanField(null=True, blank=True)
    prize_opt_in_at = models.DateTimeField(null=True, blank=True)
    poster_pdf = models.FileField(
        upload_to="posters/%Y/%m/",
        blank=True,
        validators=[FileExtensionValidator(["pdf"])],
    )
    poster_uploaded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def display_text(self):
        return self.edited_abstract_text.strip() or self.abstract_text

    @property
    def review_count(self):
        return self.review_assignments.filter(completed_at__isnull=False).count()

    @property
    def average_score(self):
        completed = []
        for assignment in self.review_assignments.select_related("review"):
            try:
                completed.append(assignment.review.score)
            except Review.DoesNotExist:
                continue
        if not completed:
            return None
        return round(sum(completed) / len(completed), 2)

    def build_action_token(self, action):
        payload = {"submission": str(self.public_id), "action": action}
        return signing.dumps(payload, salt="conference.submission.action")

    @classmethod
    def from_signed_token(cls, token, expected_action, max_age=60 * 60 * 24 * 30):
        payload = signing.loads(token, max_age=max_age, salt="conference.submission.action")
        if payload.get("action") != expected_action:
            raise signing.BadSignature("Unexpected submission action.")
        return cls.objects.get(public_id=payload["submission"])

    def can_edit(self, user):
        return user.is_authenticated and self.submitter_id == user.id and self.status == self.Status.DRAFT

    @property
    def prize_opt_in_label(self):
        if self.prize_opt_in is None:
            return "Not answered"
        return "Yes" if self.prize_opt_in else "No"

    def mark_submitted(self):
        self.status = self.Status.SUBMITTED
        self.submitted_at = timezone.now()

    def get_absolute_url(self):
        return reverse("submission-detail", args=[str(self.public_id)])

    @property
    def topic_names(self):
        return [topic.name for topic in self.topics.all()]

    @property
    def completed_review_count(self):
        return self.review_assignments.filter(completed_at__isnull=False).count()

    def recommended_reviewers(self, limit=5):
        from .roles import REVIEWER_GROUP

        topic_ids = list(self.topics.values_list("id", flat=True))
        if not topic_ids:
            return []

        assigned_ids = set(self.review_assignments.values_list("reviewer_id", flat=True))
        candidate_qs = (
            User.objects.filter(is_active=True, groups__name=REVIEWER_GROUP)
            .exclude(id__in=assigned_ids)
            .select_related("profile")
            .annotate(
                open_reviews=Count("review_assignments", filter=Q(review_assignments__completed_at__isnull=True), distinct=True),
                completed_reviews=Count("review_assignments", filter=Q(review_assignments__completed_at__isnull=False), distinct=True),
            )
            .prefetch_related(
                Prefetch(
                    "topic_expertise",
                    queryset=ReviewerTopicExpertise.objects.select_related("topic").order_by("topic__category", "topic__name"),
                )
            )
            .distinct()
        )

        suggestions = []
        for reviewer in candidate_qs:
            profile = getattr(reviewer, "profile", None)
            if profile and not profile.reviewer_is_available:
                continue

            expertise_rows = [
                expertise
                for expertise in reviewer.topic_expertise.all()
                if expertise.topic_id in topic_ids and expertise.expertise != ReviewerTopicExpertise.Expertise.AVOID
            ]
            if not expertise_rows:
                continue

            match_score = sum(expertise.expertise_weight for expertise in expertise_rows)
            max_assignments = profile.reviewer_max_assignments if profile else 6
            capacity_left = max(max_assignments - getattr(reviewer, "open_reviews", 0), 0)
            suggestions.append(
                {
                    "reviewer": reviewer,
                    "match_score": match_score,
                    "matched_topics": [expertise.topic.name for expertise in expertise_rows],
                    "open_reviews": getattr(reviewer, "open_reviews", 0),
                    "completed_reviews": getattr(reviewer, "completed_reviews", 0),
                    "capacity_left": capacity_left,
                }
            )

        suggestions.sort(
            key=lambda row: (
                row["match_score"],
                row["capacity_left"],
                -row["open_reviews"],
                row["completed_reviews"],
            ),
            reverse=True,
        )
        return suggestions[:limit]


class Author(TimeStampedModel):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="authors")
    order = models.PositiveIntegerField(default=1)
    first_name = models.CharField(max_length=128)
    middle_initial = models.CharField(max_length=16, blank=True)
    last_name = models.CharField(max_length=128)
    corresponding = models.BooleanField(default=False)
    presenting = models.BooleanField(default=False)
    institution = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=128, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        pieces = [self.first_name, self.middle_initial, self.last_name]
        return " ".join(piece for piece in pieces if piece).strip()


class ReviewAssignment(TimeStampedModel):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="review_assignments")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_assignments")
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_reviews",
    )
    note = models.CharField(max_length=255, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_reminded_at = models.DateTimeField(null=True, blank=True)
    reminder_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["completed_at", "-created_at"]
        unique_together = [("submission", "reviewer")]

    def __str__(self):
        return f"{self.submission.title} -> {self.reviewer.get_full_name() or self.reviewer.email}"

    @property
    def is_overdue(self):
        return bool(self.due_at and not self.completed_at and self.due_at < timezone.now())

    @property
    def matched_topic_names(self):
        submission_topic_ids = set(self.submission.topics.values_list("id", flat=True))
        matches = (
            self.reviewer.topic_expertise.filter(topic_id__in=submission_topic_ids)
            .exclude(expertise=ReviewerTopicExpertise.Expertise.AVOID)
            .select_related("topic")
        )
        return [match.topic.name for match in matches]

    def mark_reminded(self):
        self.last_reminded_at = timezone.now()
        self.reminder_count = (self.reminder_count or 0) + 1
        self.save(update_fields=["last_reminded_at", "reminder_count", "updated_at"])

    def save(self, *args, **kwargs):
        if not self.due_at and not self.completed_at:
            self.due_at = self.created_at + timedelta(days=14) if self.created_at else timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)


class Review(TimeStampedModel):
    class Recommendation(models.TextChoices):
        ACCEPT = "ACCEPT", "Accept"
        REVISE = "REVISE", "Revise"
        REJECT = "REJECT", "Reject"

    assignment = models.OneToOneField(ReviewAssignment, on_delete=models.CASCADE, related_name="review")
    score = models.PositiveSmallIntegerField()
    recommendation = models.CharField(max_length=16, choices=Recommendation.choices)
    suggested_topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Review for {self.assignment.submission.title}"


class CopyEditAssignment(TimeStampedModel):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="copy_edit_assignments")
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="copy_edit_assignments")
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_copy_edits",
    )
    note = models.CharField(max_length=255, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["completed_at", "-created_at"]
        unique_together = [("submission", "editor")]

    def __str__(self):
        return f"{self.submission.title} -> {self.editor.get_full_name() or self.editor.email}"


class CopyEditRecord(TimeStampedModel):
    assignment = models.OneToOneField(CopyEditAssignment, on_delete=models.CASCADE, related_name="record")
    edited_text = models.TextField()
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        return f"Copy edit for {self.assignment.submission.title}"


class ProgramSession(TimeStampedModel):
    name = models.CharField(max_length=255)
    room = models.CharField(max_length=128, blank=True)
    chair_name = models.CharField(max_length=255, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["starts_at", "name"]

    def __str__(self):
        return self.name


class ProgramSlot(TimeStampedModel):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="program_slot")
    session = models.ForeignKey(ProgramSession, on_delete=models.CASCADE, related_name="slots")
    starts_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["session__starts_at", "order", "starts_at"]

    def __str__(self):
        return f"{self.session.name}: {self.submission.title}"


@receiver(post_save, sender=User)
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
