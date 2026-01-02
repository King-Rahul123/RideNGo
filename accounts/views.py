from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from agency.models import Vehicle
from agency.views import Vehicle
from decimal import Decimal, InvalidOperation
from .models import SetAmount


def agency_account(request):
    return render(request, 'agency_accounts.html')

def Login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        identifier = request.POST.get('email_or_phone')
        password = request.POST.get('password')

        if not identifier or not password:
            messages.error(request, "Please fill out all fields.")
            return render(request, 'login.html')

        # 1. Find user by email or phone
        user_obj = User.objects.filter(email=identifier).first()
        if not user_obj:
            user_obj = User.objects.filter(last_name=identifier).first()  # phone stored in last_name

        if not user_obj:
            messages.error(request, "User does not exist!")
            return render(request, 'login.html')

        # 2. Authenticate using the real username
        user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged-in successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid password!")
            return render(request, 'login.html')

    return render(request, 'login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('agency_name')
        email = request.POST.get('email')
        last_name = request.POST.get('phone')
        password = request.POST.get('password')

        if username and password and email and last_name and first_name:
            if User.objects.filter(username=username).exists():
                messages.error(request, "User already exists.")
                return redirect('register')
            user = User.objects.create_user(username=username, first_name=first_name, email=email, last_name=last_name, password=password)
            user.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please fill out all fields.")
    return render(request, 'register.html')
    
def Logout(request):
    if not request.user.is_authenticated:
        return redirect('home')
    
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not email or not new_password or not confirm_password:
            messages.error(request, "Please fill out all fields for password reset.")
            return redirect('login')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('login')

        # Basic password strength check (you can expand)
        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('login')

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
            return redirect('login')

        # Set new password and save
        user.set_password(new_password)
        user.save()

        messages.success(request, "Password updated successfully. Please login with your new password.")
        return redirect('login')

    # If GET (or other) show login page (or redirect)
    return redirect('login')

def set_amount(request):
    agency = getattr(request.user, "agency", None)
    if not agency:
        messages.info(request, "You don't have an agency profile yet.")
        vehicles = Vehicle.objects.none()
    else:
        try:
            vehicles = agency.vehicles.all()
        except Exception:
            vehicles = Vehicle.objects.filter(agency=agency)
    if request.method == "POST":
        vehicle_value = request.POST.get('vehicle_id') or request.POST.get('vehicle') or ''
        if not vehicle_value:
            messages.error(request, "No vehicle selected.")
            return render(request, 'set_amount.html', {"vehicles": vehicles})

        # try to find vehicle by v_number first, then by pk
        vehicle = Vehicle.objects.filter(v_number=vehicle_value).first()
        if not vehicle:
            try:
                vehicle = Vehicle.objects.get(pk=vehicle_value)
            except Exception:
                vehicle = None

        if not vehicle:
            messages.error(request, "Selected vehicle not found.")
            return render(request, 'set_amount.html', {"vehicles": vehicles})

        # Helper to parse decimals safely
        def parse_decimal(val, default=Decimal('0.00')):
            if val is None or str(val).strip() == '':
                return default
            try:
                return Decimal(str(val))
            except (InvalidOperation, ValueError):
                return default

        def parse_int(val, default=0):
            try:
                return int(val)
            except (TypeError, ValueError):
                return default

        # Manual amount (required by your UI)
        manual_amount = request.POST.get('manual_amount', '').strip()
        if manual_amount == '':
            messages.error(request, "Manual Amount is required.")
            return render(request, 'set_amount.html', {"vehicles": vehicles})
        manual_amount_dec = parse_decimal(manual_amount, Decimal('0.00'))
        if manual_amount_dec < 0:
            messages.error(request, "Manual Amount must be >= 0.")
            return render(request, 'set_amount.html', {"vehicles": vehicles})

        # Determine if fixed pricing is intended
        # Handle both possible radio names used in various snippets:
        pricing_mode = request.POST.get('pricing_mode') or request.POST.get('mode') or ''
        # Also support detection if 'mode_fixed' name was posted
        is_fixed = False
        if request.POST.get('mode_fixed') == 'fixed' or pricing_mode == 'fixed' or request.POST.get('pricing_mode') == 'fixed' or request.POST.get('mode_fixed'):
            is_fixed = True
        # (if the radio posts nothing, we still accept manual-only)

        # Fixed per-km fields
        min_km = parse_int(request.POST.get('min_km', 0), 0)
        amount_per_km = parse_decimal(request.POST.get('amount_per_km', 0), Decimal('0.00'))

        # Flat fields
        flat_amount = parse_decimal(request.POST.get('flat_amount', 0), Decimal('0.00'))
        flat_max_km = parse_int(request.POST.get('flat_max_km', 0), 0)
        extra_after_flat_per_km = parse_decimal(request.POST.get('extra_after_flat_per_km', 0), Decimal('0.00'))

        # Extra charges
        night_charge = parse_decimal(request.POST.get('night_charge', 0), Decimal('0.00'))
        tax_percent = parse_decimal(request.POST.get('tax_percent', 0), Decimal('0.00'))
        other_charges = parse_decimal(request.POST.get('other_charges', 0), Decimal('0.00'))

        note = request.POST.get('note', '').strip()

        # Basic server-side validations (mirror your JS)
        if is_fixed:
            # if per-km is selected (JS ensures min_km and amount_per_km validity),
            # here we do lightweight checks.
            if request.POST.get('fixed_type') == 'per_km' or request.POST.get('fixed_per_km') or request.POST.get('fixed_type') == 'per_km':
                if min_km < 1:
                    messages.error(request, "Minimum KM for fixed per-km must be >= 1.")
                    return render(request, 'set_amount.html', {"vehicles": vehicles})
                if amount_per_km < 0:
                    messages.error(request, "Amount per KM must be >= 0.")
                    return render(request, 'set_amount.html', {"vehicles": vehicles})
            elif request.POST.get('fixed_type') == 'flat' or request.POST.get('fixed_flat') or request.POST.get('fixed_type') == 'flat':
                if flat_amount < 0:
                    messages.error(request, "Flat amount must be >= 0.")
                    return render(request, 'set_amount.html', {"vehicles": vehicles})
                if flat_max_km <= 0:
                    messages.error(request, "Flat max KM must be an integer > 0.")
                    return render(request, 'set_amount.html', {"vehicles": vehicles})

            # tax percent sanity check
            if tax_percent < 0 or tax_percent > 100:
                messages.error(request, "Tax percent must be between 0 and 100.")
                return render(request, 'set_amount.html', {"vehicles": vehicles})

        # Save or update the SetAmount instance
        try:
            obj, created = SetAmount.objects.update_or_create(
                vehicle=vehicle,
                defaults={
                    'manual_amount': manual_amount_dec,
                    'is_fixed': is_fixed,
                    'min_km': min_km,
                    'amount_per_km': amount_per_km,
                    'flat_amount': flat_amount,
                    'flat_max_km': flat_max_km,
                    'extra_after_flat_per_km': extra_after_flat_per_km,
                    'night_charge': night_charge,
                    'tax_percent': tax_percent,
                    'other_charges': other_charges,
                    'note': note,
                }
            )
        except Exception as e:
            messages.error(request, f"Error saving pricing: {e}")
            return render(request, 'set_amount.html', {"vehicles": vehicles})

        messages.success(request, "Pricing saved successfully.")
        return redirect('set_amount')  # or redirect to same view route name

    return render(request, 'set_amount.html', {"vehicles": vehicles})

# Helper to parse decimals safely
def parse_decimal(val, default=Decimal('0.00')):
    if val is None or str(val).strip() == '':
        return default
    try:
        return Decimal(str(val))
    except (InvalidOperation, ValueError):
        return default
