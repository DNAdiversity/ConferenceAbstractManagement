from django.conf import settings

from .services import submission_deadline_context


def conference_meta(request):
    deadline_context = submission_deadline_context()
    return {
        "conference_name": getattr(settings, "CONFERENCE_NAME", "Minimal Conference Abstract Management"),
        "conference_time_zone": getattr(settings, "CONFERENCE_TIME_ZONE", settings.TIME_ZONE),
        "abstract_word_limit": getattr(settings, "ABSTRACT_WORD_LIMIT", 300),
        **deadline_context,
    }
