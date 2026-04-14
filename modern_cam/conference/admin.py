from collections import defaultdict
from datetime import timedelta

from django.conf import settings
from django.contrib import admin, messages
from django.core.mail import send_mail
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.utils.html import format_html, format_html_join

from .models import (
    Author,
    CopyEditAssignment,
    CopyEditRecord,
    ProgramSession,
    ProgramSlot,
    Review,
    ReviewAssignment,
    ReviewerTopicExpertise,
    Submission,
    Topic,
    UserProfile,
)
from .roles import COPY_EDITOR_GROUP, REVIEWER_GROUP, users_in_group


admin.site.site_header = "Minimal Conference Admin"
admin.site.site_title = "Minimal Conference Admin"
admin.site.index_title = "Operations Console"


STATUS_TONES = {
    Submission.Status.DRAFT: "#7f94a2",
    Submission.Status.SUBMITTED: "#44dec8",
    Submission.Status.UNDER_REVIEW: "#84e1ff",
    Submission.Status.REVIEWED: "#c4ed8a",
    Submission.Status.ASSIGNED_FOR_EDIT: "#ffd580",
    Submission.Status.EDITED: "#ffb085",
    Submission.Status.SCHEDULED: "#f77b93",
    Submission.Status.FINALIZED: "#c6b3ff",
}


def render_badge(label, color):
    return format_html(
        '<span style="display:inline-flex;align-items:center;padding:.28rem .62rem;'
        'border-radius:999px;border:1px solid {0};color:{0};font-size:.75rem;'
        'font-weight:600;letter-spacing:.02em;">{1}</span>',
        color,
        label,
    )


def _send_reviewer_digest(reviewer, assignments, acting_user):
    if not reviewer.email or not assignments:
        return False

    subject = f"Review reminder: {len(assignments)} abstract review(s) still open"
    due_lines = []
    for assignment in assignments:
        due_label = assignment.due_at.strftime("%b %d, %Y") if assignment.due_at else "No due date"
        due_lines.append(f"- {assignment.submission.title} (due {due_label})")

    body = "\n".join(
        [
            f"Hello {reviewer.get_full_name() or reviewer.email},",
            "",
            "This is a reminder that the following abstract reviews are still open:",
            *due_lines,
            "",
            "Please sign in to the conference system to complete your reviews.",
            "",
            f"Sent by: {acting_user.get_full_name() or acting_user.email or acting_user.username}",
        ]
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [reviewer.email], fail_silently=False)

    reminder_time = timezone.now()
    for assignment in assignments:
        assignment.last_reminded_at = reminder_time
        assignment.reminder_count = (assignment.reminder_count or 0) + 1
        assignment.updated_at = reminder_time
    ReviewAssignment.objects.bulk_update(assignments, ["last_reminded_at", "reminder_count", "updated_at"])
    return True


class ReviewerScopedMixin:
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "reviewer":
            kwargs["queryset"] = users_in_group(REVIEWER_GROUP)
        if db_field.name == "editor":
            kwargs["queryset"] = users_in_group(COPY_EDITOR_GROUP)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class AuthorInline(admin.TabularInline):
    model = Author
    extra = 0


class ReviewAssignmentInline(ReviewerScopedMixin, admin.TabularInline):
    model = ReviewAssignment
    extra = 0
    fields = ("reviewer", "assigned_by", "due_at", "note", "completed_at", "last_reminded_at", "reminder_count")
    readonly_fields = ("completed_at", "last_reminded_at", "reminder_count")


class CopyEditAssignmentInline(ReviewerScopedMixin, admin.TabularInline):
    model = CopyEditAssignment
    extra = 0
    fields = ("editor", "assigned_by", "note", "completed_at")
    readonly_fields = ("completed_at",)


class ReviewerTopicExpertiseInline(ReviewerScopedMixin, admin.TabularInline):
    model = ReviewerTopicExpertise
    extra = 0
    fields = ("reviewer", "expertise", "notes")


class ProgramSlotInline(admin.TabularInline):
    model = ProgramSlot
    extra = 0


class ReviewStateFilter(admin.SimpleListFilter):
    title = "review state"
    parameter_name = "review_state"

    def lookups(self, request, model_admin):
        return (
            ("open", "Open"),
            ("overdue", "Overdue"),
            ("completed", "Completed"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "open":
            return queryset.filter(completed_at__isnull=True)
        if self.value() == "overdue":
            return queryset.filter(completed_at__isnull=True, due_at__lt=now)
        if self.value() == "completed":
            return queryset.filter(completed_at__isnull=False)
        return queryset


@admin.action(description="Auto-assign best topic-matched reviewers")
def auto_assign_topic_matched_reviewers(modeladmin, request, queryset):
    created_total = 0
    skipped_total = 0
    for submission in queryset.prefetch_related("topics"):
        existing_count = submission.review_assignments.count()
        needed = max(2 - existing_count, 0)
        if needed == 0:
            skipped_total += 1
            continue

        suggestions = [row for row in submission.recommended_reviewers(limit=6) if row["capacity_left"] > 0]
        if not suggestions:
            skipped_total += 1
            continue

        created_for_submission = 0
        for suggestion in suggestions[:needed]:
            assignment, created = ReviewAssignment.objects.get_or_create(
                submission=submission,
                reviewer=suggestion["reviewer"],
                defaults={
                    "assigned_by": request.user,
                    "note": f"Auto-matched from topic expertise: {', '.join(suggestion['matched_topics'])}",
                    "due_at": timezone.now() + timedelta(days=14),
                },
            )
            if created:
                created_total += 1
                created_for_submission += 1

        if created_for_submission and submission.status == Submission.Status.SUBMITTED:
            submission.status = Submission.Status.UNDER_REVIEW
            submission.save(update_fields=["status", "updated_at"])

    if created_total:
        modeladmin.message_user(request, f"Created {created_total} reviewer assignment(s).", level=messages.SUCCESS)
    if skipped_total:
        modeladmin.message_user(
            request,
            f"{skipped_total} submission(s) were skipped because they already had enough reviewers or no topic match was available.",
            level=messages.INFO,
        )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "submitter_name",
        "presentation_type",
        "status_badge",
        "topic_summary",
        "review_progress",
        "average_score_display",
        "suggested_reviewer_count",
        "submitted_at",
    )
    list_filter = ("status", "presentation_type", "topics")
    search_fields = (
        "title",
        "submitter__email",
        "submitter__first_name",
        "submitter__last_name",
        "authors__first_name",
        "authors__last_name",
    )
    readonly_fields = (
        "public_id",
        "submitted_at",
        "average_score_display",
        "reviewer_suggestions_panel",
        "public_action_links",
    )
    inlines = [AuthorInline, ReviewAssignmentInline, CopyEditAssignmentInline]
    filter_horizontal = ("topics",)
    actions = [auto_assign_topic_matched_reviewers]
    date_hierarchy = "submitted_at"

    fieldsets = (
        (
            "Submission",
            {
                "fields": (
                    "public_id",
                    "submitter",
                    "title",
                    "presentation_type",
                    "status",
                    "topics",
                    "submitted_at",
                )
            },
        ),
        ("Abstract", {"fields": ("abstract_text", "edited_abstract_text", "decision_notes")}),
        (
            "Operations",
            {
                "fields": (
                    "average_score_display",
                    "reviewer_suggestions_panel",
                    "public_action_links",
                )
            },
        ),
        (
            "Public follow-up",
            {
                "fields": (
                    "presenter_confirmed_author",
                    "presenter_confirmed_at",
                    "prize_opt_in",
                    "prize_opt_in_at",
                    "poster_pdf",
                    "poster_uploaded_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("submitter")
            .prefetch_related("topics", "review_assignments", "authors")
        )

    @admin.display(ordering="submitter__last_name", description="Submitter")
    def submitter_name(self, obj):
        return obj.submitter.get_full_name() or obj.submitter.email

    @admin.display(description="Status")
    def status_badge(self, obj):
        return render_badge(obj.get_status_display(), STATUS_TONES.get(obj.status, "#9aa8b2"))

    @admin.display(description="Topics")
    def topic_summary(self, obj):
        return ", ".join(obj.topic_names[:3]) or "No topics"

    @admin.display(description="Review progress")
    def review_progress(self, obj):
        assigned = obj.review_assignments.count()
        completed = obj.completed_review_count
        return f"{completed}/{assigned or 0} completed"

    @admin.display(description="Average score")
    def average_score_display(self, obj):
        if not obj:
            return "Not reviewed"
        return obj.average_score if obj.average_score is not None else "Not reviewed"

    @admin.display(description="Suggested matches")
    def suggested_reviewer_count(self, obj):
        return len(obj.recommended_reviewers(limit=3))

    @admin.display(description="Reviewer recommendations")
    def reviewer_suggestions_panel(self, obj):
        if not obj or not obj.pk:
            return "Save the submission before loading reviewer suggestions."

        suggestions = obj.recommended_reviewers(limit=5)
        if not suggestions:
            expertise_url = reverse("admin:conference_reviewertopicexpertise_changelist")
            return format_html(
                'No strong topic matches yet. <a href="{}">Configure reviewer expertise</a> to unlock recommendations.',
                expertise_url,
            )

        rows = format_html_join(
            "",
            (
                '<li style="margin-bottom:.5rem;">'
                '<a href="{}">{}</a> '
                '<span style="color:#6c7a86;">score {}, open {}, capacity left {}</span>'
                '<br><span style="color:#6c7a86;">Matched topics: {}</span>'
                "</li>"
            ),
            (
                (
                    reverse("admin:auth_user_change", args=[row["reviewer"].pk]),
                    row["reviewer"].get_full_name() or row["reviewer"].email,
                    row["match_score"],
                    row["open_reviews"],
                    row["capacity_left"],
                    ", ".join(row["matched_topics"]),
                )
                for row in suggestions
            ),
        )
        return format_html("<ul style='margin:0;padding-left:1.2rem;'>{}</ul>", rows)

    @admin.display(description="Signed follow-up links")
    def public_action_links(self, obj):
        if not obj or not obj.pk:
            return "Save the submission before generating public links."

        presenter = reverse("public-presenter", args=[obj.build_action_token("presenter")])
        prize = reverse("public-prize", args=[obj.build_action_token("prize")])
        poster = reverse("public-poster", args=[obj.build_action_token("poster")])
        return format_html(
            '<a href="{0}" target="_blank">Presenter link</a><br>'
            '<a href="{1}" target="_blank">Prize link</a><br>'
            '<a href="{2}" target="_blank">Poster link</a>',
            presenter,
            prize,
            poster,
        )


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "is_active", "submission_count", "reviewer_count")
    list_filter = ("category", "is_active")
    search_fields = ("category", "name")
    inlines = [ReviewerTopicExpertiseInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            submission_total=Count("submissions", distinct=True),
            reviewer_total=Count(
                "reviewer_expertise",
                filter=~Q(reviewer_expertise__expertise=ReviewerTopicExpertise.Expertise.AVOID),
                distinct=True,
            ),
        )

    @admin.display(ordering="submission_total", description="Submissions")
    def submission_count(self, obj):
        return obj.submission_total

    @admin.display(ordering="reviewer_total", description="Reviewers")
    def reviewer_count(self, obj):
        return obj.reviewer_total


@admin.register(ReviewerTopicExpertise)
class ReviewerTopicExpertiseAdmin(ReviewerScopedMixin, admin.ModelAdmin):
    list_display = ("reviewer_name", "topic", "expertise", "notes")
    list_filter = ("expertise", "topic__category")
    search_fields = ("reviewer__email", "reviewer__first_name", "reviewer__last_name", "topic__name")

    @admin.display(ordering="reviewer__last_name", description="Reviewer")
    def reviewer_name(self, obj):
        return obj.reviewer.get_full_name() or obj.reviewer.email


@admin.register(ReviewAssignment)
class ReviewAssignmentAdmin(ReviewerScopedMixin, admin.ModelAdmin):
    list_display = (
        "submission",
        "reviewer_name",
        "state_badge",
        "due_at",
        "topic_overlap",
        "reviewer_workload",
        "reminder_count",
        "last_reminded_at",
    )
    list_filter = (ReviewStateFilter, "due_at", "reviewer")
    search_fields = ("submission__title", "reviewer__email", "reviewer__first_name", "reviewer__last_name")
    actions = ("send_reminder_email", "extend_due_dates_by_one_week")

    @admin.display(ordering="reviewer__last_name", description="Reviewer")
    def reviewer_name(self, obj):
        return obj.reviewer.get_full_name() or obj.reviewer.email

    @admin.display(description="State")
    def state_badge(self, obj):
        if obj.completed_at:
            return render_badge("Completed", "#6bbf8b")
        if obj.is_overdue:
            return render_badge("Overdue", "#f77b93")
        return render_badge("Open", "#44dec8")

    @admin.display(description="Topic overlap")
    def topic_overlap(self, obj):
        names = obj.matched_topic_names
        return ", ".join(names) if names else "No mapped expertise"

    @admin.display(description="Open workload")
    def reviewer_workload(self, obj):
        profile = getattr(obj.reviewer, "profile", None)
        max_assignments = profile.reviewer_max_assignments if profile else 6
        open_reviews = obj.reviewer.review_assignments.filter(completed_at__isnull=True).count()
        return f"{open_reviews}/{max_assignments}"

    @admin.action(description="Send reminder email for selected open assignments")
    def send_reminder_email(self, request, queryset):
        grouped = defaultdict(list)
        for assignment in queryset.select_related("reviewer", "submission"):
            if assignment.completed_at:
                continue
            grouped[assignment.reviewer].append(assignment)

        sent_count = 0
        for reviewer, assignments in grouped.items():
            if _send_reviewer_digest(reviewer, assignments, request.user):
                sent_count += 1

        if sent_count:
            self.message_user(request, f"Sent reminder emails to {sent_count} reviewer(s).", level=messages.SUCCESS)
        else:
            self.message_user(request, "No reminder emails were sent.", level=messages.WARNING)

    @admin.action(description="Extend due dates by one week")
    def extend_due_dates_by_one_week(self, request, queryset):
        updated = 0
        for assignment in queryset:
            if assignment.completed_at:
                continue
            assignment.due_at = (assignment.due_at or timezone.now()) + timedelta(days=7)
            assignment.save(update_fields=["due_at", "updated_at"])
            updated += 1
        self.message_user(request, f"Extended {updated} assignment due date(s).", level=messages.SUCCESS)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("submission_title", "reviewer_name", "score", "recommendation", "submitted_at")
    list_filter = ("recommendation", "score", "suggested_topic")
    search_fields = ("assignment__submission__title", "assignment__reviewer__email")

    @admin.display(ordering="assignment__submission__title", description="Submission")
    def submission_title(self, obj):
        return obj.assignment.submission.title

    @admin.display(ordering="assignment__reviewer__last_name", description="Reviewer")
    def reviewer_name(self, obj):
        return obj.assignment.reviewer.get_full_name() or obj.assignment.reviewer.email


@admin.register(CopyEditAssignment)
class CopyEditAssignmentAdmin(ReviewerScopedMixin, admin.ModelAdmin):
    list_display = ("submission", "editor_name", "assigned_by", "completed_at")
    list_filter = ("completed_at",)
    search_fields = ("submission__title", "editor__email")

    @admin.display(ordering="editor__last_name", description="Editor")
    def editor_name(self, obj):
        return obj.editor.get_full_name() or obj.editor.email


@admin.register(CopyEditRecord)
class CopyEditRecordAdmin(admin.ModelAdmin):
    list_display = ("assignment", "completed_at")


@admin.register(ProgramSession)
class ProgramSessionAdmin(admin.ModelAdmin):
    list_display = ("name", "room", "chair_name", "starts_at", "ends_at", "slot_count")
    inlines = [ProgramSlotInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(slot_total=Count("slots", distinct=True))

    @admin.display(ordering="slot_total", description="Slots")
    def slot_count(self, obj):
        return obj.slot_total


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "institution",
        "country",
        "reviewer_is_available",
        "reviewer_max_assignments",
        "reviewer_open_assignments",
        "expertise_link",
    )
    list_filter = ("country", "reviewer_is_available")
    search_fields = ("user__email", "user__first_name", "user__last_name", "institution")
    readonly_fields = ("expertise_summary",)
    fieldsets = (
        (
            "Profile",
            {
                "fields": (
                    "user",
                    "salutation",
                    "institution",
                    "department",
                    "country",
                    "address_line_1",
                    "address_line_2",
                    "city",
                    "province_state",
                    "postal_code",
                )
            },
        ),
        (
            "Reviewer Operations",
            {
                "fields": (
                    "reviewer_is_available",
                    "reviewer_max_assignments",
                    "reviewer_notes",
                    "expertise_summary",
                )
            },
        ),
    )

    @admin.display(description="Topic expertise")
    def expertise_summary(self, obj):
        if not obj:
            return "Save the profile before adding reviewer expertise."
        expertise_rows = obj.user.topic_expertise.select_related("topic").exclude(
            expertise=ReviewerTopicExpertise.Expertise.AVOID
        )
        if not expertise_rows.exists():
            change_url = reverse("admin:conference_reviewertopicexpertise_add")
            return format_html(
                'No topic expertise configured. <a href="{}">Add reviewer-topic mappings</a>.',
                change_url,
            )
        return format_html_join(
            "<br>",
            "{} · {}",
            ((row.topic.name, row.get_expertise_display()) for row in expertise_rows),
        )

    @admin.display(description="Expertise")
    def expertise_link(self, obj):
        url = f'{reverse("admin:conference_reviewertopicexpertise_changelist")}?reviewer__id__exact={obj.user_id}'
        count = obj.user.topic_expertise.count()
        return format_html('<a href="{}">{} mapped</a>', url, count)


def conference_operations_dashboard(request):
    submissions = (
        Submission.objects.select_related("submitter")
        .prefetch_related("topics")
        .annotate(
            assigned_reviews=Count("review_assignments", distinct=True),
            completed_reviews=Count("review_assignments", filter=Q(review_assignments__completed_at__isnull=False), distinct=True),
        )
        .order_by("-updated_at")
    )
    triage_rows = []
    for submission in submissions.filter(
        status__in=[
            Submission.Status.SUBMITTED,
            Submission.Status.UNDER_REVIEW,
            Submission.Status.REVIEWED,
            Submission.Status.ASSIGNED_FOR_EDIT,
            Submission.Status.EDITED,
        ]
    )[:12]:
        triage_rows.append(
            {
                "submission": submission,
                "suggestions": submission.recommended_reviewers(limit=3),
                "admin_url": reverse("admin:conference_submission_change", args=[submission.pk]),
            }
        )

    overdue_assignments = (
        ReviewAssignment.objects.filter(completed_at__isnull=True, due_at__lt=timezone.now())
        .select_related("submission", "reviewer")
        .order_by("due_at")[:10]
    )
    topic_rows = (
        Topic.objects.annotate(
            submission_total=Count("submissions", distinct=True),
            reviewer_total=Count(
                "reviewer_expertise",
                filter=~Q(reviewer_expertise__expertise=ReviewerTopicExpertise.Expertise.AVOID),
                distinct=True,
            ),
        )
        .order_by("-submission_total", "category", "name")[:10]
    )
    status_rows = [
        {"label": label, "count": Submission.objects.filter(status=value).count(), "color": STATUS_TONES.get(value, "#9aa8b2")}
        for value, label in Submission.Status.choices
    ]

    context = {
        **admin.site.each_context(request),
        "title": "Conference operations",
        "status_rows": status_rows,
        "triage_rows": triage_rows,
        "overdue_assignments": overdue_assignments,
        "topic_rows": topic_rows,
    }
    return TemplateResponse(request, "admin/conference/operations_dashboard.html", context)


def conference_reviewer_dashboard(request):
    reviewers = (
        users_in_group(REVIEWER_GROUP)
        .select_related("profile")
        .annotate(
            open_reviews=Count("review_assignments", filter=Q(review_assignments__completed_at__isnull=True), distinct=True),
            overdue_reviews=Count(
                "review_assignments",
                filter=Q(review_assignments__completed_at__isnull=True, review_assignments__due_at__lt=timezone.now()),
                distinct=True,
            ),
            completed_reviews=Count("review_assignments", filter=Q(review_assignments__completed_at__isnull=False), distinct=True),
        )
        .prefetch_related(
            Prefetch(
                "topic_expertise",
                queryset=ReviewerTopicExpertise.objects.select_related("topic").exclude(
                    expertise=ReviewerTopicExpertise.Expertise.AVOID
                ),
            )
        )
    )

    reviewer_rows = []
    for reviewer in reviewers:
        reviewer_rows.append(
            {
                "reviewer": reviewer,
                "profile": reviewer.profile,
                "topic_labels": [
                    f"{row.topic.name} ({row.get_expertise_display()})" for row in reviewer.topic_expertise.all()
                ],
                "assignments_url": (
                    f'{reverse("admin:conference_reviewassignment_changelist")}?reviewer__id__exact={reviewer.pk}'
                ),
                "topic_url": (
                    f'{reverse("admin:conference_reviewertopicexpertise_changelist")}?reviewer__id__exact={reviewer.pk}'
                ),
                "remind_url": reverse("admin:conference-reviewer-remind", args=[reviewer.pk]),
            }
        )

    context = {
        **admin.site.each_context(request),
        "title": "Reviewer operations",
        "reviewer_rows": reviewer_rows,
    }
    return TemplateResponse(request, "admin/conference/reviewer_dashboard.html", context)


def conference_reviewer_remind(request, user_id):
    redirect_to = request.META.get("HTTP_REFERER") or reverse("admin:conference-reviewer-dashboard")
    if request.method != "POST":
        return HttpResponseRedirect(redirect_to)

    reviewer = users_in_group(REVIEWER_GROUP).filter(pk=user_id).first()
    if not reviewer:
        messages.error(request, "Reviewer not found.")
        return HttpResponseRedirect(redirect_to)

    assignments = list(
        ReviewAssignment.objects.filter(reviewer=reviewer, completed_at__isnull=True).select_related("submission")
    )
    if not assignments:
        messages.info(request, "That reviewer has no open assignments.")
        return HttpResponseRedirect(redirect_to)

    if _send_reviewer_digest(reviewer, assignments, request.user):
        messages.success(request, f"Reminder sent to {reviewer.get_full_name() or reviewer.email}.")
    else:
        messages.warning(request, "No reminder was sent because the reviewer does not have an email address.")
    return HttpResponseRedirect(redirect_to)


def conference_agenda_dashboard(request):
    sessions = ProgramSession.objects.prefetch_related(
        Prefetch(
            "slots",
            queryset=ProgramSlot.objects.select_related("submission").order_by("order", "starts_at", "created_at"),
        )
    ).order_by("starts_at")
    unscheduled = (
        Submission.objects.select_related("submitter")
        .prefetch_related("topics")
        .annotate(completed_reviews=Count("review_assignments", filter=Q(review_assignments__completed_at__isnull=False)))
        .filter(
            program_slot__isnull=True,
            status__in=[
                Submission.Status.REVIEWED,
                Submission.Status.ASSIGNED_FOR_EDIT,
                Submission.Status.EDITED,
                Submission.Status.SCHEDULED,
            ],
        )
        .order_by("-updated_at")
    )

    context = {
        **admin.site.each_context(request),
        "title": "Agenda assembly",
        "sessions": sessions,
        "unscheduled": unscheduled,
        "add_session_url": reverse("admin:conference_programsession_add"),
    }
    return TemplateResponse(request, "admin/conference/agenda_dashboard.html", context)


def conference_agenda_schedule(request, submission_id):
    redirect_to = request.META.get("HTTP_REFERER") or reverse("admin:conference-agenda-dashboard")
    if request.method != "POST":
        return HttpResponseRedirect(redirect_to)

    submission = Submission.objects.filter(pk=submission_id).first()
    session = ProgramSession.objects.filter(pk=request.POST.get("session")).first()
    if not submission or not session:
        messages.error(request, "Select a valid submission and session before scheduling.")
        return HttpResponseRedirect(redirect_to)

    starts_at = None
    starts_at_raw = (request.POST.get("starts_at") or "").strip()
    if starts_at_raw:
        starts_at = parse_datetime(starts_at_raw)
        if starts_at and timezone.is_naive(starts_at):
            starts_at = timezone.make_aware(starts_at, timezone.get_current_timezone())

    try:
        order = max(int(request.POST.get("order") or 1), 1)
    except ValueError:
        order = 1

    ProgramSlot.objects.update_or_create(
        submission=submission,
        defaults={"session": session, "starts_at": starts_at, "order": order},
    )
    submission.status = Submission.Status.SCHEDULED
    submission.save(update_fields=["status", "updated_at"])
    messages.success(request, f"Scheduled “{submission.title}” into {session.name}.")
    return HttpResponseRedirect(redirect_to)


def _custom_admin_urls():
    return [
        path("conference/operations/", admin.site.admin_view(conference_operations_dashboard), name="conference-operations-dashboard"),
        path("conference/reviewers/", admin.site.admin_view(conference_reviewer_dashboard), name="conference-reviewer-dashboard"),
        path(
            "conference/reviewers/<int:user_id>/remind/",
            admin.site.admin_view(conference_reviewer_remind),
            name="conference-reviewer-remind",
        ),
        path("conference/agenda/", admin.site.admin_view(conference_agenda_dashboard), name="conference-agenda-dashboard"),
        path(
            "conference/agenda/schedule/<int:submission_id>/",
            admin.site.admin_view(conference_agenda_schedule),
            name="conference-agenda-schedule",
        ),
    ]


if not hasattr(admin.site, "_conference_console_urls_patched"):
    _original_get_urls = admin.site.get_urls

    def get_urls():
        return _custom_admin_urls() + _original_get_urls()

    admin.site.get_urls = get_urls
    admin.site._conference_console_urls_patched = True
