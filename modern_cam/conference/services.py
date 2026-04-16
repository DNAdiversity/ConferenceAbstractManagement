import re
from datetime import datetime
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone


WORD_RE = re.compile(r"\b[\w'-]+\b")


def count_words(value):
    return len(WORD_RE.findall((value or "").strip()))


def conference_zone():
    return ZoneInfo(getattr(settings, "CONFERENCE_TIME_ZONE", settings.TIME_ZONE))


def parse_deadline(raw_value, fallback_tz):
    if not raw_value:
        return None
    parsed = datetime.fromisoformat(raw_value)
    if timezone.is_naive(parsed):
        parsed = parsed.replace(tzinfo=fallback_tz)
    return parsed.astimezone(fallback_tz)


def submission_deadline():
    return getattr(settings, "SUBMISSION_DEADLINE", None)


def submission_window_is_open(now=None):
    deadline = submission_deadline()
    if not deadline:
        return True
    return (now or timezone.now()) <= deadline


def submission_deadline_context(now=None):
    deadline = submission_deadline()
    if not deadline:
        return {
            "submission_deadline": None,
            "submission_deadline_is_open": True,
            "submission_deadline_label": "Rolling submissions",
            "submission_deadline_state": "open",
        }

    tz = conference_zone()
    localized_deadline = deadline.astimezone(tz)
    localized_now = (now or timezone.now()).astimezone(tz)
    remaining = localized_deadline - localized_now

    if remaining.total_seconds() <= 0:
        state = "closed"
        label = "Submission window closed"
    elif remaining.days >= 7:
        state = "open"
        label = f"{remaining.days} day{'s' if remaining.days != 1 else ''} remaining"
    elif remaining.days >= 1:
        state = "closing"
        label = f"{remaining.days} day{'s' if remaining.days != 1 else ''} left"
    else:
        hours = max(int(remaining.total_seconds() // 3600), 1)
        state = "closing"
        label = f"{hours} hour{'s' if hours != 1 else ''} left"

    return {
        "submission_deadline": localized_deadline,
        "submission_deadline_is_open": remaining.total_seconds() > 0,
        "submission_deadline_label": label,
        "submission_deadline_state": state,
    }


def receipt_url(request, submission):
    relative = reverse("submission-receipt", args=[submission.public_id])
    if request is None:
        return relative
    return request.build_absolute_uri(relative)


def send_submission_receipt(submission, request=None, actor=None, note=""):
    from .models import SubmissionNotification

    if not submission.submitter.email:
        return None

    subject = f"Submission receipt: {submission.reference_code}"
    receipt_link = receipt_url(request, submission)
    topic_list = ", ".join(submission.topic_names) or "No topics selected"
    author_names = ", ".join(author.full_name for author in submission.authors.order_by("order", "id"))

    body = "\n".join(
        [
            f"Conference submission receipt for {submission.reference_code}",
            "",
            f"Title: {submission.title}",
            f"Presentation type: {submission.get_presentation_type_display()}",
            f"Status: {submission.get_status_display()}",
            f"Topics: {topic_list}",
            f"Authors: {author_names}",
            f"Submitted at: {timezone.localtime(submission.submitted_at).strftime('%Y-%m-%d %H:%M %Z') if submission.submitted_at else 'Draft only'}",
            f"Co-author approval certified: {'Yes' if submission.submitter_certified_authors_approved else 'No'}",
            "",
            f"Receipt link: {receipt_link}",
            "",
            "Keep this email for your records. You can also re-open the receipt from your dashboard.",
        ]
    )

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [submission.submitter.email],
        fail_silently=False,
    )

    return SubmissionNotification.objects.create(
        submission=submission,
        kind=SubmissionNotification.Kind.SUBMISSION_RECEIPT,
        recipient=submission.submitter.email,
        subject=subject,
        sent_by=actor,
        note=note,
    )
