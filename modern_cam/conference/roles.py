from django.contrib.auth.models import Group, User


ORGANIZER_GROUP = "Organizers"
REVIEWER_GROUP = "Reviewers"
COPY_EDITOR_GROUP = "Copy Editors"

ROLE_GROUPS = [ORGANIZER_GROUP, REVIEWER_GROUP, COPY_EDITOR_GROUP]


def ensure_role_groups():
    for group_name in ROLE_GROUPS:
        Group.objects.get_or_create(name=group_name)


def has_group(user, group_name):
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name=group_name).exists()


def users_in_group(group_name):
    return User.objects.filter(is_active=True, groups__name=group_name).distinct().order_by("first_name", "last_name", "email")
