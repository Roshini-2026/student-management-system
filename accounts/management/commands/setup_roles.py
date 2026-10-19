from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

# role -> {app name: [permission codenames]}
ROLES = {
    "Admin": {
        "core": ["view_student", "add_student", "change_student", "delete_student", "view_reports"],
        "auth": ["view_user", "add_user", "change_user", "delete_user"],
    },
    "Staff": {"core": ["view_student", "add_student", "change_student"]},
    "Viewer": {"core": ["view_student"]},
}


class Command(BaseCommand):
    help = "Create the Admin, Staff and Viewer groups and give each its permissions."

    def handle(self, *args, **options):
        for role, apps in ROLES.items():
            group, _ = Group.objects.get_or_create(name=role)
            permissions = []
            for app_label, codenames in apps.items():
                permissions += Permission.objects.filter(
                    content_type__app_label=app_label, codename__in=codenames
                )
            group.permissions.set(permissions)  # replaces the old list, so re-running is safe
            if options["verbosity"]:
                self.stdout.write(f"{role}: {len(permissions)} permissions")