from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("submissions/new/", views.submission_create, name="submission-create"),
    path("submissions/<uuid:public_id>/", views.submission_detail, name="submission-detail"),
    path("submissions/<uuid:public_id>/receipt/", views.submission_receipt, name="submission-receipt"),
    path("submissions/<uuid:public_id>/resend-receipt/", views.resend_submission_receipt, name="submission-resend-receipt"),
    path("submissions/<uuid:public_id>/edit/", views.submission_edit, name="submission-edit"),
    path("organizer/submissions/", views.organizer_submission_list, name="organizer-submission-list"),
    path("organizer/submissions/<uuid:public_id>/", views.organizer_submission_detail, name="organizer-submission-detail"),
    path("organizer/submissions/<uuid:public_id>/assign-reviewer/", views.assign_reviewer, name="assign-reviewer"),
    path("organizer/submissions/<uuid:public_id>/assign-editor/", views.assign_copy_editor, name="assign-editor"),
    path("organizer/submissions/<uuid:public_id>/create-session/", views.create_program_session, name="create-program-session"),
    path("organizer/submissions/<uuid:public_id>/schedule/", views.schedule_submission, name="schedule-submission"),
    path("reviews/<int:assignment_id>/", views.review_assignment_detail, name="review-assignment-detail"),
    path("copy-edits/<int:assignment_id>/", views.copy_edit_assignment_detail, name="copy-edit-assignment-detail"),
    path("agenda/", views.agenda, name="agenda"),
    path("public/presenter/<str:token>/", views.public_presenter_confirm, name="public-presenter"),
    path("public/prize/<str:token>/", views.public_prize_choice, name="public-prize"),
    path("public/poster/<str:token>/", views.public_poster_upload, name="public-poster"),
]
