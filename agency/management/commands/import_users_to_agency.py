# agency/management/commands/import_users_to_agency.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from agency.models import Agency
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = "Create Agency records for existing users that do not have one (skips superusers)."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be created without saving.')
        parser.add_argument('--map-phone-from-lastname', action='store_true',
                            help='If true, map phone from User.last_name (useful if you stored phone there).')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        map_phone_from_lastname = options['map_phone_from_lastname']

        users = User.objects.filter(is_superuser=False)
        created_count = 0
        skipped_count = 0

        for u in users:
            if hasattr(u, 'agency') and u.agency is not None:
                skipped_count += 1
                continue

            agency_name = (u.first_name or "").strip() or u.username
            email = u.email or ""
            phone = (u.last_name or "").strip() if map_phone_from_lastname else ""

            self.stdout.write(f"Would create Agency for user={u.username} -> agency_name='{agency_name}', phone='{phone}', email='{email}'")
            if not dry_run:
                with transaction.atomic():
                    Agency.objects.create(user=u, agency_name=agency_name, email=email, phone=phone)
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Done. Created: {created_count}, Skipped (already had agency): {skipped_count}"))
