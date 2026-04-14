from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from conference.models import ProgramSession, ReviewerTopicExpertise, Topic
from conference.roles import COPY_EDITOR_GROUP, ORGANIZER_GROUP, REVIEWER_GROUP, ensure_role_groups


TOPICS = [
    ("Biodiversity", "DNA Barcoding"),
    ("Biodiversity", "Freshwater Monitoring"),
    ("Genomics", "Environmental DNA"),
    ("Genomics", "Metabarcoding"),
    ("Methods", "Data Standards"),
    ("Methods", "Reference Libraries"),
]


class Command(BaseCommand):
    help = "Create role groups, starter topics, and optional demo accounts."

    def add_arguments(self, parser):
        parser.add_argument("--with-demo-users", action="store_true")

    def handle(self, *args, **options):
        ensure_role_groups()

        for category, name in TOPICS:
            Topic.objects.get_or_create(category=category, name=name)

        ProgramSession.objects.get_or_create(
            name="Opening Plenary",
            defaults={
                "room": "Harbour Hall",
                "chair_name": "Conference Chair",
                "starts_at": timezone.now().replace(hour=9, minute=0, second=0, microsecond=0),
                "ends_at": timezone.now().replace(hour=10, minute=30, second=0, microsecond=0),
                "description": "Kick-off session for keynote talks.",
            },
        )

        if options["with_demo_users"]:
            admin_user = self._create_admin("admin@example.org", "Admin", "User")
            organizer = self._create_user("organizer@example.org", "Organizer", "One", ORGANIZER_GROUP)
            reviewer = self._create_user("reviewer@example.org", "Reviewer", "One", REVIEWER_GROUP)
            editor = self._create_user("editor@example.org", "Copy", "Editor", COPY_EDITOR_GROUP)
            reviewer.profile.reviewer_max_assignments = 8
            reviewer.profile.reviewer_is_available = True
            reviewer.profile.save(update_fields=["reviewer_max_assignments", "reviewer_is_available", "updated_at"])
            self._seed_reviewer_expertise(reviewer)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created demo users: {admin_user.email}, {organizer.email}, {reviewer.email}, {editor.email}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Seed data is ready."))

    def _create_user(self, email, first_name, last_name, group_name):
        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email, "first_name": first_name, "last_name": last_name},
        )
        if created:
            user.set_password("change-me-now")
            user.save()
        user.groups.add(Group.objects.get(name=group_name))
        return user

    def _create_admin(self, email, first_name, last_name):
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password("change-me-now")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    def _seed_reviewer_expertise(self, reviewer):
        expertise_map = {
            "DNA Barcoding": ReviewerTopicExpertise.Expertise.LEAD,
            "Environmental DNA": ReviewerTopicExpertise.Expertise.EXPERIENCED,
            "Metabarcoding": ReviewerTopicExpertise.Expertise.EXPERIENCED,
            "Freshwater Monitoring": ReviewerTopicExpertise.Expertise.EMERGING,
        }
        for topic in Topic.objects.all():
            expertise = expertise_map.get(topic.name)
            if not expertise:
                continue
            ReviewerTopicExpertise.objects.get_or_create(
                reviewer=reviewer,
                topic=topic,
                defaults={"expertise": expertise},
            )
