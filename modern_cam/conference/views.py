from collections import defaultdict

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    AuthorFormSet,
    CopyEditAssignmentForm,
    CopyEditRecordForm,
    PresenterConfirmationForm,
    PosterUploadForm,
    PrizeChoiceForm,
    ProfileForm,
    ProgramSessionForm,
    RegistrationForm,
    ReviewForm,
    ReviewerAssignmentForm,
    ScheduleSubmissionForm,
    SubmissionForm,
)
from .models import (
    CopyEditAssignment,
    CopyEditRecord,
    ProgramSession,
    ProgramSlot,
    Review,
    ReviewAssignment,
    SubmissionNotification,
    SubmissionSnapshot,
    Submission,
    Topic,
)
from .roles import COPY_EDITOR_GROUP, ORGANIZER_GROUP, REVIEWER_GROUP, has_group
from .services import send_submission_receipt, submission_deadline_context, submission_window_is_open
from .tokens import submission_from_token


def organizer_required(view_func):
    return login_required(user_passes_test(lambda user: has_group(user, ORGANIZER_GROUP))(view_func))


def reviewer_required(view_func):
    return login_required(user_passes_test(lambda user: has_group(user, REVIEWER_GROUP))(view_func))


def copy_editor_required(view_func):
    return login_required(user_passes_test(lambda user: has_group(user, COPY_EDITOR_GROUP))(view_func))


def home(request):
    upcoming_sessions = ProgramSession.objects.prefetch_related("slots__submission").order_by("starts_at")[:4]
    stats = Submission.objects.aggregate(
        submissions=Count("id"),
        submitted=Count("id", filter=Q(status__in=[Submission.Status.SUBMITTED, Submission.Status.UNDER_REVIEW, Submission.Status.REVIEWED, Submission.Status.ASSIGNED_FOR_EDIT, Submission.Status.EDITED, Submission.Status.SCHEDULED, Submission.Status.FINALIZED])),
        scheduled=Count("id", filter=Q(status__in=[Submission.Status.SCHEDULED, Submission.Status.FINALIZED])),
    )
    topics = Topic.objects.filter(is_active=True).order_by("category", "name")[:8]
    return render(
        request,
        "conference/home.html",
        {
            "stats": stats,
            "topics": topics,
            "upcoming_sessions": upcoming_sessions,
        },
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            for field, value in profile_form.cleaned_data.items():
                setattr(user.profile, field, value)
            user.profile.save()
            login(request, user)
            messages.success(request, "Your account is ready. You can start a draft abstract right away.")
            return redirect("dashboard")
    else:
        form = RegistrationForm()
        profile_form = ProfileForm()

    return render(
        request,
        "registration/register.html",
        {
            "form": form,
            "profile_form": profile_form,
        },
    )


@login_required
def dashboard(request):
    submissions = (
        Submission.objects.filter(submitter=request.user)
        .prefetch_related("topics", "authors", "review_assignments__review", "copy_edit_assignments")
        .order_by("-updated_at")
    )
    review_assignments = (
        ReviewAssignment.objects.filter(reviewer=request.user)
        .select_related("submission", "review")
        .order_by("completed_at", "-created_at")
    )
    copy_edit_assignments = (
        CopyEditAssignment.objects.filter(editor=request.user)
        .select_related("submission")
        .order_by("completed_at", "-created_at")
    )

    submission_counts = {
        "total": submissions.count(),
        "drafts": submissions.filter(status=Submission.Status.DRAFT).count(),
        "active": submissions.filter(
            status__in=[
                Submission.Status.SUBMITTED,
                Submission.Status.UNDER_REVIEW,
                Submission.Status.REVIEWED,
                Submission.Status.ASSIGNED_FOR_EDIT,
                Submission.Status.EDITED,
            ]
        ).count(),
        "scheduled": submissions.filter(
            status__in=[Submission.Status.SCHEDULED, Submission.Status.FINALIZED]
        ).count(),
    }
    assignment_counts = {
        "review_open": review_assignments.filter(completed_at__isnull=True).count(),
        "review_done": review_assignments.filter(completed_at__isnull=False).count(),
        "edit_open": copy_edit_assignments.filter(completed_at__isnull=True).count(),
        "edit_done": copy_edit_assignments.filter(completed_at__isnull=False).count(),
    }

    organizer_stats = None
    recent_submissions = None
    if has_group(request.user, ORGANIZER_GROUP):
        organizer_stats = {
            "submitted": Submission.objects.filter(status=Submission.Status.SUBMITTED).count(),
            "under_review": Submission.objects.filter(status=Submission.Status.UNDER_REVIEW).count(),
            "edited": Submission.objects.filter(status=Submission.Status.EDITED).count(),
            "scheduled": Submission.objects.filter(status=Submission.Status.SCHEDULED).count(),
        }
        recent_submissions = Submission.objects.select_related("submitter").order_by("-updated_at")[:8]

    return render(
        request,
        "conference/dashboard.html",
        {
            "submissions": submissions,
            "review_assignments": review_assignments,
            "copy_edit_assignments": copy_edit_assignments,
            "submission_counts": submission_counts,
            "assignment_counts": assignment_counts,
            "organizer_stats": organizer_stats,
            "recent_submissions": recent_submissions,
            "is_organizer": has_group(request.user, ORGANIZER_GROUP),
            "is_reviewer": has_group(request.user, REVIEWER_GROUP),
            "is_copy_editor": has_group(request.user, COPY_EDITOR_GROUP),
        },
    )


@login_required
def submission_create(request):
    submission = Submission(submitter=request.user)
    return _submission_form(request, submission, create=True)


@login_required
def submission_edit(request, public_id):
    submission = get_object_or_404(Submission.objects.prefetch_related("authors", "topics"), public_id=public_id)
    if not submission.can_edit(request.user):
        raise PermissionDenied("This abstract can no longer be edited by the submitter.")
    return _submission_form(request, submission, create=False)


def _submission_form(request, submission, create):
    if request.method == "POST":
        form = SubmissionForm(request.POST, instance=submission)
        formset = AuthorFormSet(request.POST, instance=submission, prefix="authors")
        is_submit_intent = "submit_submission" in request.POST
        if form.is_valid() and formset.is_valid():
            if is_submit_intent and not submission_window_is_open():
                deadline_info = submission_deadline_context()
                form.add_error(
                    None,
                    "The abstract deadline closed on "
                    f"{deadline_info['submission_deadline'].strftime('%b %d, %Y at %I:%M %p %Z')}."
                )
            if is_submit_intent and not form.cleaned_data.get("certify_authors_approved"):
                form.add_error(
                    "certify_authors_approved",
                    "Please confirm that every listed author approved this abstract before submitting.",
                )

        if form.is_valid() and formset.is_valid() and not form.errors:
            draft = form.save(commit=False)
            draft.submitter = request.user
            if is_submit_intent:
                draft.submitter_certified_authors_approved = True
                draft.submitter_certified_authors_approved_at = timezone.now()
            draft.save()
            form.save_m2m()
            formset.instance = draft
            formset.save()
            _normalize_author_order(draft)
            if is_submit_intent:
                draft.mark_submitted()
                draft.save(
                    update_fields=[
                        "status",
                        "submitted_at",
                        "submitter_certified_authors_approved",
                        "submitter_certified_authors_approved_at",
                        "updated_at",
                    ]
                )
                draft.create_snapshot(
                    SubmissionSnapshot.EventType.SUBMITTED,
                    actor=request.user,
                    note="Submitted for review",
                )
                send_submission_receipt(
                    draft,
                    request=request,
                    actor=request.user,
                    note="Initial submission receipt",
                )
                messages.success(request, "Your abstract has been submitted for review.")
            else:
                draft.create_snapshot(
                    SubmissionSnapshot.EventType.DRAFT_SAVED,
                    actor=request.user,
                    note="Draft saved",
                )
                messages.success(request, "Draft saved.")
            return redirect("submission-detail", draft.public_id)
    else:
        form = SubmissionForm(instance=submission)
        formset = AuthorFormSet(instance=submission, prefix="authors")

    return render(
        request,
        "conference/submission_form.html",
        {
            "form": form,
            "formset": formset,
            "submission": submission,
            "page_title": "Start a new abstract" if create else "Edit draft abstract",
            "submission_deadline_info": submission_deadline_context(),
        },
    )


def _normalize_author_order(submission):
    for index, author in enumerate(submission.authors.order_by("order", "id"), start=1):
        if author.order != index:
            author.order = index
            author.save(update_fields=["order"])


def _user_can_view_submission(user, submission):
    if not user.is_authenticated:
        return False
    if has_group(user, ORGANIZER_GROUP):
        return True
    if submission.submitter_id == user.id:
        return True
    if submission.review_assignments.filter(reviewer=user).exists():
        return True
    if submission.copy_edit_assignments.filter(editor=user).exists():
        return True
    return False


@login_required
def submission_detail(request, public_id):
    submission = get_object_or_404(
        Submission.objects.select_related("submitter", "presenter_confirmed_author")
        .prefetch_related(
            "topics",
            "authors",
            "snapshots",
            "notifications",
            Prefetch("review_assignments", queryset=ReviewAssignment.objects.select_related("reviewer", "review")),
            Prefetch("copy_edit_assignments", queryset=CopyEditAssignment.objects.select_related("editor", "record")),
        ),
        public_id=public_id,
    )
    if not _user_can_view_submission(request.user, submission):
        raise PermissionDenied("You do not have access to this abstract.")

    public_links = {
        "presenter": request.build_absolute_uri(reverse("public-presenter", args=[submission.build_action_token("presenter")])),
        "prize": request.build_absolute_uri(reverse("public-prize", args=[submission.build_action_token("prize")])),
        "poster": request.build_absolute_uri(reverse("public-poster", args=[submission.build_action_token("poster")])),
    }

    return render(
        request,
        "conference/submission_detail.html",
        {
            "submission": submission,
            "public_links": public_links,
            "is_organizer": has_group(request.user, ORGANIZER_GROUP),
            "can_edit_submission": submission.can_edit(request.user),
            "can_manage_receipts": request.user.id == submission.submitter_id or has_group(request.user, ORGANIZER_GROUP),
            "latest_receipt": submission.latest_submission_snapshot,
            "receipt_notifications": submission.notifications.filter(
                kind=SubmissionNotification.Kind.SUBMISSION_RECEIPT
            )[:5],
        },
    )


@login_required
def submission_receipt(request, public_id):
    submission = get_object_or_404(
        Submission.objects.select_related("submitter")
        .prefetch_related("topics", "authors", "snapshots", "notifications"),
        public_id=public_id,
    )
    if not _user_can_view_submission(request.user, submission):
        raise PermissionDenied("You do not have access to this submission receipt.")

    receipt_snapshot = submission.latest_submission_snapshot
    if receipt_snapshot is None:
        messages.info(request, "A submission receipt will appear after the abstract is submitted.")
        return redirect("submission-detail", public_id)

    return render(
        request,
        "conference/submission_receipt.html",
        {
            "submission": submission,
            "receipt_snapshot": receipt_snapshot,
            "receipt_notifications": submission.notifications.filter(
                kind=SubmissionNotification.Kind.SUBMISSION_RECEIPT
            )[:10],
        },
    )


@login_required
def resend_submission_receipt(request, public_id):
    submission = get_object_or_404(Submission.objects.select_related("submitter"), public_id=public_id)
    if not (request.user.id == submission.submitter_id or has_group(request.user, ORGANIZER_GROUP)):
        raise PermissionDenied("You do not have permission to resend this receipt.")
    if request.method != "POST":
        return redirect("submission-detail", public_id)
    if submission.status == Submission.Status.DRAFT:
        messages.info(request, "Drafts do not have formal submission receipts yet.")
        return redirect("submission-detail", public_id)

    send_submission_receipt(
        submission,
        request=request,
        actor=request.user,
        note="Receipt resent from submission detail",
    )
    submission.create_snapshot(
        SubmissionSnapshot.EventType.RECEIPT_RESENT,
        actor=request.user,
        note="Receipt resent",
    )
    messages.success(request, "Submission receipt resent.")
    return redirect("submission-detail", public_id)


@organizer_required
def organizer_submission_list(request):
    qs = Submission.objects.select_related("submitter").prefetch_related("topics").order_by("-updated_at")
    status_filter = request.GET.get("status", "").strip()
    search = request.GET.get("q", "").strip()
    if status_filter:
        qs = qs.filter(status=status_filter)
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(submitter__email__icontains=search))

    return render(
        request,
        "conference/organizer_submission_list.html",
        {
            "submissions": qs,
            "status_filter": status_filter,
            "search": search,
            "status_choices": Submission.Status.choices,
        },
    )


@organizer_required
def organizer_submission_detail(request, public_id):
    submission = get_object_or_404(
        Submission.objects.select_related("submitter", "program_slot__session", "presenter_confirmed_author")
        .prefetch_related(
            "topics",
            "authors",
            Prefetch("review_assignments", queryset=ReviewAssignment.objects.select_related("reviewer", "review")),
            Prefetch("copy_edit_assignments", queryset=CopyEditAssignment.objects.select_related("editor", "record")),
        ),
        public_id=public_id,
    )
    reviewer_form = ReviewerAssignmentForm()
    editor_form = CopyEditAssignmentForm()
    session_form = ProgramSessionForm()
    schedule_form = ScheduleSubmissionForm(instance=getattr(submission, "program_slot", None))
    public_links = {
        "presenter": request.build_absolute_uri(reverse("public-presenter", args=[submission.build_action_token("presenter")])),
        "prize": request.build_absolute_uri(reverse("public-prize", args=[submission.build_action_token("prize")])),
        "poster": request.build_absolute_uri(reverse("public-poster", args=[submission.build_action_token("poster")])),
    }

    return render(
        request,
        "conference/organizer_submission_detail.html",
        {
            "submission": submission,
            "reviewer_form": reviewer_form,
            "editor_form": editor_form,
            "session_form": session_form,
            "schedule_form": schedule_form,
            "public_links": public_links,
        },
    )


@organizer_required
def assign_reviewer(request, public_id):
    submission = get_object_or_404(Submission, public_id=public_id)
    form = ReviewerAssignmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        assignment, created = ReviewAssignment.objects.get_or_create(
            submission=submission,
            reviewer=form.cleaned_data["reviewer"],
            defaults={"assigned_by": request.user, "note": form.cleaned_data["note"]},
        )
        if created:
            if submission.status == Submission.Status.SUBMITTED:
                submission.status = Submission.Status.UNDER_REVIEW
                submission.save(update_fields=["status", "updated_at"])
            messages.success(request, "Reviewer assigned.")
        else:
            messages.info(request, "That reviewer is already assigned.")
    return redirect("organizer-submission-detail", public_id)


@organizer_required
def assign_copy_editor(request, public_id):
    submission = get_object_or_404(Submission, public_id=public_id)
    form = CopyEditAssignmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        assignment, created = CopyEditAssignment.objects.get_or_create(
            submission=submission,
            editor=form.cleaned_data["editor"],
            defaults={"assigned_by": request.user, "note": form.cleaned_data["note"]},
        )
        if created:
            submission.status = Submission.Status.ASSIGNED_FOR_EDIT
            submission.save(update_fields=["status", "updated_at"])
            messages.success(request, "Copy editor assigned.")
        else:
            messages.info(request, "That copy editor is already assigned.")
    return redirect("organizer-submission-detail", public_id)


@organizer_required
def create_program_session(request, public_id):
    form = ProgramSessionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        session = form.save()
        messages.success(request, f"Program session '{session.name}' created.")
    return redirect("organizer-submission-detail", public_id)


@organizer_required
def schedule_submission(request, public_id):
    submission = get_object_or_404(Submission, public_id=public_id)
    current_slot = getattr(submission, "program_slot", None)
    form = ScheduleSubmissionForm(request.POST or None, instance=current_slot)
    if request.method == "POST" and form.is_valid():
        slot = form.save(commit=False)
        slot.submission = submission
        slot.save()
        submission.status = Submission.Status.SCHEDULED
        submission.save(update_fields=["status", "updated_at"])
        messages.success(request, "Abstract scheduled on the agenda.")
    return redirect("organizer-submission-detail", public_id)


@login_required
def review_assignment_detail(request, assignment_id):
    assignment = get_object_or_404(ReviewAssignment.objects.select_related("submission", "review"), pk=assignment_id)
    if not (assignment.reviewer_id == request.user.id or has_group(request.user, ORGANIZER_GROUP)):
        raise PermissionDenied("This review assignment does not belong to you.")

    review = getattr(assignment, "review", None)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.assignment = assignment
            review.submitted_at = timezone.now()
            review.save()
            assignment.completed_at = timezone.now()
            assignment.save(update_fields=["completed_at", "updated_at"])
            assignment.submission.status = Submission.Status.REVIEWED
            assignment.submission.save(update_fields=["status", "updated_at"])
            messages.success(request, "Review submitted.")
            return redirect("dashboard")
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "conference/review_assignment_detail.html",
        {
            "assignment": assignment,
            "form": form,
        },
    )


@login_required
def copy_edit_assignment_detail(request, assignment_id):
    assignment = get_object_or_404(CopyEditAssignment.objects.select_related("submission", "record"), pk=assignment_id)
    if not (assignment.editor_id == request.user.id or has_group(request.user, ORGANIZER_GROUP)):
        raise PermissionDenied("This copy-edit assignment does not belong to you.")

    record = getattr(assignment, "record", None)
    if request.method == "POST":
        form = CopyEditRecordForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save(commit=False)
            record.assignment = assignment
            record.completed_at = timezone.now()
            record.save()
            assignment.completed_at = timezone.now()
            assignment.save(update_fields=["completed_at", "updated_at"])
            submission = assignment.submission
            submission.edited_abstract_text = record.edited_text
            submission.status = Submission.Status.EDITED
            submission.save(update_fields=["edited_abstract_text", "status", "updated_at"])
            submission.create_snapshot(
                SubmissionSnapshot.EventType.COPY_EDIT_COMPLETED,
                actor=request.user,
                note="Copy edit completed",
            )
            messages.success(request, "Copy edit saved.")
            return redirect("dashboard")
    else:
        form = CopyEditRecordForm(instance=record, initial={"edited_text": assignment.submission.display_text})

    return render(
        request,
        "conference/copy_edit_assignment_detail.html",
        {
            "assignment": assignment,
            "form": form,
        },
    )


def agenda(request):
    sessions = ProgramSession.objects.prefetch_related("slots__submission__authors").order_by("starts_at")
    grouped = defaultdict(list)
    for session in sessions:
        key = session.starts_at.date()
        grouped[key].append(session)
    return render(request, "conference/agenda.html", {"grouped_sessions": dict(grouped)})


def public_presenter_confirm(request, token):
    submission = submission_from_token(token, "presenter")
    if submission is None:
        messages.error(request, "That presenter confirmation link is invalid or has expired.")
        return redirect("home")

    if request.method == "POST":
        form = PresenterConfirmationForm(submission, request.POST)
        if form.is_valid():
            submission.presenter_confirmed_author = form.cleaned_data["author"]
            submission.presenter_confirmed_at = timezone.now()
            submission.save(update_fields=["presenter_confirmed_author", "presenter_confirmed_at", "updated_at"])
            submission.create_snapshot(
                SubmissionSnapshot.EventType.PRESENTER_CONFIRMED,
                actor_label=form.cleaned_data["author"].full_name,
                note="Presenter confirmed via secure link",
            )
            messages.success(request, "Presenter confirmation saved.")
            return redirect("home")
    else:
        initial_author = submission.presenter_confirmed_author or submission.authors.filter(presenting=True).first()
        form = PresenterConfirmationForm(submission, initial={"author": initial_author})

    return render(
        request,
        "conference/public_presenter_confirm.html",
        {
            "submission": submission,
            "form": form,
        },
    )


def public_prize_choice(request, token):
    submission = submission_from_token(token, "prize")
    if submission is None:
        messages.error(request, "That prize response link is invalid or has expired.")
        return redirect("home")

    if request.method == "POST":
        form = PrizeChoiceForm(request.POST)
        if form.is_valid():
            submission.prize_opt_in = form.cleaned_data["participating"] == "yes"
            submission.prize_opt_in_at = timezone.now()
            submission.save(update_fields=["prize_opt_in", "prize_opt_in_at", "updated_at"])
            submission.create_snapshot(
                SubmissionSnapshot.EventType.PRIZE_UPDATED,
                actor_label="Signed public link",
                note=f"Prize preference set to {submission.prize_opt_in_label.lower()}",
            )
            messages.success(request, "Prize preference saved.")
            return redirect("home")
    else:
        initial = None
        if submission.prize_opt_in is not None:
            initial = "yes" if submission.prize_opt_in else "no"
        form = PrizeChoiceForm(initial={"participating": initial})

    return render(
        request,
        "conference/public_prize_choice.html",
        {
            "submission": submission,
            "form": form,
        },
    )


def public_poster_upload(request, token):
    submission = submission_from_token(token, "poster")
    if submission is None:
        messages.error(request, "That poster upload link is invalid or has expired.")
        return redirect("home")

    if request.method == "POST":
        form = PosterUploadForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.poster_uploaded_at = timezone.now()
            submission.save(update_fields=["poster_pdf", "poster_uploaded_at", "updated_at"])
            submission.create_snapshot(
                SubmissionSnapshot.EventType.POSTER_UPLOADED,
                actor_label="Signed public link",
                note="Poster uploaded",
            )
            messages.success(request, "Poster PDF uploaded.")
            return redirect("home")
    else:
        form = PosterUploadForm(instance=submission)

    return render(
        request,
        "conference/public_poster_upload.html",
        {
            "submission": submission,
            "form": form,
        },
    )
