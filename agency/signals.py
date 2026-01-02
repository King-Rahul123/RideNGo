# agency/signals.py
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.db import transaction
from .models import Agency

User = get_user_model()

@receiver(user_logged_in)
def ensure_agency_on_login(sender, user, request, **kwargs):
    """
    Ensure a non-superuser has an Agency record after they login.
    Runs at each login but only creates if missing.
    """
    # skip superusers/staff if you don't want them to get agencies
    if user.is_superuser:
        return

    # If Agency already exists, do nothing
    if hasattr(user, "agency") and user.agency is not None:
        return

    # Map user fields to Agency fields — adjust if your project stores phone in last_name etc.
    agency_name = (user.first_name or "").strip() or user.username
    email = user.email or ""
    # YOUR CASE: you have phone numbers in last_name per your screenshot — use last_name as fallback:
    phone = (user.last_name or "").strip()

    # Create Agency if none exists for this user
    # Wrap in transaction to be safe with concurrent logins
    with transaction.atomic():
        Agency.objects.get_or_create(
            user=user,
            defaults={
                "agency_name": agency_name,
                "email": email,
                "phone": phone,
            },
        )
