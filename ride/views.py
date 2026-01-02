# views.py (add this)
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Booking, BookingStatus
from agency.models import Agency, Vehicle
from django.utils.dateparse import parse_date, parse_time
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST
import random
import time

# ---------- Constants ----------
OTP_LENGTH = 6
OTP_EXPIRE_SECONDS = 5 * 60  # 5 minutes

SESSION_OTP_KEY = "otp_value"
SESSION_OTP_MOBILE = "otp_mobile"
SESSION_OTP_EXPIRES = "otp_expires_at"
SESSION_OTP_VERIFIED = "otp_verified"

# ---------- Utilities ----------
def _generate_otp():
    start = 10 ** (OTP_LENGTH - 1)
    return str(random.randint(start, start * 10 - 1))


def send_sms_mock(mobile, otp):
    # dev fallback — prints to server console
    print(f"[MOCK SMS] Sending OTP {otp} to {mobile}")


def _format_indian_mobile(mobile_raw: str) -> str:
    if not mobile_raw:
        return ""
    m = mobile_raw.strip()
    # remove spaces and hyphens first
    m = m.replace(" ", "").replace("-", "")
    # if exactly 10 digits, add +91
    if m.isdigit() and len(m) == 10:
        return "+91" + m
    # if starts with 91 and 12 chars -> +91...
    if m.startswith("91") and len(m) == 12:
        return "+" + m
    # if already has + and digits, return as-is
    return m


# Create your views here.
def booking(request):
    agencies = Agency.objects.all()
    vehicles = Vehicle.objects.values("id","v_type","agency_id","v_model","v_seat")
    return render(request,"booking.html",{
        "agencies":agencies,
        "vehicles":list(vehicles)
    })

def status(request):
    return render(request, 'book_status.html')

def get_vehicles(request):
    v_type = request.GET.get("v_type")
    agency = request.GET.get("agency")
    seats = request.GET.get("seats")

    vehicles = Vehicle.objects.all()

    if v_type:
        vehicles = vehicles.filter(v_type=v_type)

    if agency:
        vehicles = vehicles.filter(agency_id=agency)

    if seats:
        vehicles = vehicles.filter(seats=seats)

    data = list(vehicles.values("id","v_model","seats","v_type"))
    return JsonResponse({"vehicles": data})


# map frontend v_type values to Booking.VEHICLE_TYPES keys
VTYPE_MAP = {
    "car": "CAR",
    "tourist-bus(mini)": "TRAVELLER_MINI",
    "tourist-bus": "TOURIST_BUS",
    "luxury-bus": "LUXURY",
}

# ---------- API 1: Return seats for selected v_type ----------
def api_seats(request):
    v_type = request.GET.get("v_type")
    if not v_type:
        return JsonResponse({"error": "v_type is required"}, status=400)

    vehicles = Vehicle.objects.filter(v_type__iexact=v_type)
    seats = sorted({v.seats for v in vehicles if v.seats})

    return JsonResponse(seats, safe=False)


# ---------- API 2: Return agencies based on v_type + seats ----------
def api_agencies(request):
    v_type = request.GET.get("type")
    seats = request.GET.get("seats")

    qs = Agency.objects.all()

    # agency → vehicle → filter
    if v_type or seats:
        qs = qs.filter(vehicle__isnull=False).distinct()

        if v_type:
            qs = qs.filter(vehicle__v_type__iexact=v_type)

        if seats:
            qs = qs.filter(vehicle__seats=str(seats))

    data = [{"id": a.id, "agency_name": a.agency_name} for a in qs]
    return JsonResponse(data, safe=False)


# ---------- API 3: Return car models based on agency + seats ----------
def api_models(request):
    agency_id = request.GET.get("agency")
    seats = request.GET.get("seats")

    if not agency_id:
        return JsonResponse([], safe=False)

    vehicles = Vehicle.objects.filter(agency_id=agency_id)

    if seats:
        vehicles = vehicles.filter(seats=str(seats))

    model_list = []

    for v in vehicles:
        model_list.append({
            "id": v.id,
            "name": v.v_model,
        })

    return JsonResponse(model_list, safe=False)

def create_booking(request):
    if request.method == "POST":
        # collect from POST (names from booking.html)
        v_type = request.POST.get("v_type", "").strip()
        v_seat = request.POST.get("seats", "").strip()
        agency = request.POST.get("travellers")  # service provider select
        v_model = request.POST.get("v_model", "").strip()
        address = request.POST.get("pickup", "").strip()
        booking_from = request.POST.get("fromDate", "").strip()
        booking_to = request.POST.get("toDate", "").strip()
        purpose = request.POST.get("purpose", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        destination = request.POST.get("destination", "").strip()
        pickup_time = request.POST.get("pickupTime", "").strip()
        amount_raw = request.POST.get("amount", "").replace("₹", "").replace(",", "").strip()
        notes = request.POST.get("notes", "").strip()

        # Basic validation
        if not (v_type and agency and address and booking_from and booking_to and purpose and mobile and v_seat and v_model):
            messages.error(request, "Please fill all required fields.")
            return redirect('booking')  # or show form with errors

        # Map v_type to DB choice
        v_type = VTYPE_MAP.get(v_type.lower())
        if not v_type:
            # fallback: try uppercase
            v_type = v_type.upper()

    # parse dates / time
    try:
        booking_from_date = parse_date(booking_from)
        booking_to_date = parse_date(booking_to)
        pickup_time_parsed = parse_time(pickup_time) if pickup_time else None
    except Exception:
        messages.error(request, "Invalid date/time format.")
        return redirect('booking')

    try:
        v_seat = Vehicle.objects.get(pk=v_seat)
    except:
        messages.error(request, "Choose vehicle type")
    # find agency
    try:
        agency = Agency.objects.get(pk=agency)
    except Agency.DoesNotExist:
        messages.error(request, "Selected service provider not found.")
        return redirect('booking')

    # Try to link a vehicle: match by agency, model, seats and type (best-effort)
    vehicle = None
    try:
        vehicle_qs = Vehicle.objects.filter(
            agency=agency,
            v_model__iexact=v_model,
            seats=v_seat,
        )
        # if your Vehicle has a v_type field, add v_type filter too (some projects call it v_type or v_category)
        if hasattr(Vehicle, "v_type"):
            vehicle_qs = vehicle_qs.filter(v_type__iexact=v_type)
        vehicle = vehicle_qs.first()
    except Exception:
        vehicle = None

    # parse amount
    amount = 0
    try:
        amount = float(amount_raw) if amount_raw else 0
    except ValueError:
        amount = 0

    # create booking
    booking = Booking(
        agency=agency,
        vehicle=vehicle,
        v_type=v_type,
        v_seat=v_seat,
        v_model=v_model,
        pickup_address=address,
        destination=destination,
        booking_from=booking_from_date,
        booking_to=booking_to_date,
        pickup_time=pickup_time_parsed,
        purpose=purpose,
        mobile=mobile,
        amount=amount,
        notes=notes or None,
    )
    booking.save()
    messages.success(request, "Booking submitted successfully.")
    return redirect('booking')

def api_models(request):
    agency_id = request.GET.get("agency")
    seats = request.GET.get("seats")

    if not agency_id:
        return JsonResponse([], safe=False)

    vehicles = Vehicle.objects.filter(agency_id=agency_id)

    if seats:
        vehicles = vehicles.filter(seats=str(seats))

    model_list = []

    for v in vehicles:
        model_list.append({
            "id": v.id,
            "name": v.v_model,
        })

    return JsonResponse(model_list, safe=False)

def api_vehicles(request):
    v_type = request.GET.get("v_type", "").strip()
    seats = request.GET.get("seats", "").strip()
    agency_id = request.GET.get("agency", "").strip()

    qs = Vehicle.objects.select_related('agency').all()

    if v_type:
        qs = qs.filter(v_type__iexact=v_type)
    if seats:
        # seats may be stored as int or string; try both
        qs = qs.filter(seats=str(seats))
    if agency_id:
        qs = qs.filter(agency_id=agency_id)

    result = []
    for v in qs:
        result.append({
            "id": v.id,
            "v_model": v.v_model,
            "plate": getattr(v, "plate_no", "") or getattr(v, "plate", ""),
            "seats": v.seats,
            "v_type": getattr(v, "v_type", ""),
            "agency_id": v.agency_id,
            "agency_name": v.agency.agency_name if v.agency else "",
            # if you store an image field, include its URL
            "image": (v.image.url if hasattr(v, "image") and getattr(v, "image") else None),
            # add any other fields useful to show on frontend
        })

    return JsonResponse(result, safe=False)

# ---------- OTP endpoints ----------
@require_POST
def send_otp(request):
    mobile_raw = request.POST.get("mobile", "").strip()
    mobile = _format_indian_mobile(mobile_raw)
    if not mobile:
        return JsonResponse({"ok": False, "error": "Mobile number is required"}, status=400)

    # generate OTP and save to session
    otp = _generate_otp()
    now_ts = int(time.time())
    expires_ts = now_ts + OTP_EXPIRE_SECONDS

    request.session[SESSION_OTP_KEY] = otp
    request.session[SESSION_OTP_MOBILE] = mobile
    request.session[SESSION_OTP_EXPIRES] = expires_ts
    request.session.pop(SESSION_OTP_VERIFIED, None)
    request.session.modified = True

    # attempt to send via Twilio if enabled, otherwise use mock
    if getattr(settings, "USE_TWILIO", False):
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Your OTP is {otp}. It expires in {OTP_EXPIRE_SECONDS//60} minutes.",
                from_=settings.TWILIO_FROM_NUMBER,
                to=mobile
            )
        except Exception as e:
            # if sending fails, return error and keep OTP in session for debugging
            return JsonResponse({"ok": False, "error": f"Failed to send OTP: {str(e)}"}, status=500)
    else:
        # dev fallback
        send_sms_mock(mobile, otp)

    # if DEBUG, include otp in response (only for dev)
    resp = {"ok": True, "message": "OTP sent successfully"}
    if getattr(settings, "DEBUG", False):
        resp["otp"] = otp
    return JsonResponse(resp)


@require_POST
def verify_otp(request):
    mobile_raw = request.POST.get("mobile", "").strip()
    otp_in = request.POST.get("otp", "").strip()

    mobile = _format_indian_mobile(mobile_raw)
    sess_mobile = request.session.get(SESSION_OTP_MOBILE)
    sess_otp = request.session.get(SESSION_OTP_KEY)
    sess_expires = request.session.get(SESSION_OTP_EXPIRES, 0)
    now = int(time.time())

    if not sess_mobile or not sess_otp:
        return JsonResponse({"ok": False, "error": "No OTP requested for this session"}, status=400)
    if sess_mobile != mobile:
        return JsonResponse({"ok": False, "error": "Mobile mismatch"}, status=400)
    if now > int(sess_expires):
        return JsonResponse({"ok": False, "error": "OTP expired"}, status=400)
    if otp_in != sess_otp:
        return JsonResponse({"ok": False, "error": "Invalid OTP"}, status=400)

    request.session[SESSION_OTP_VERIFIED] = True
    request.session["verified_mobile"] = mobile
    request.session.modified = True
    return JsonResponse({"ok": True})

def booking_status_view(request):
    if request.method == 'POST':
        if not request.session.get('otp_verified'):
            messages.error(request, "Please verify mobile via OTP before submitting booking status.")
            return redirect('booking_status')
        mobile = request.session.get('verified_mobile')
        booking_id = request.POST.get('booking_id', '').strip()
        status = request.POST.get('status', 'pending').strip()
        driver_name = request.POST.get('driver_name', '').strip()
        remarks = request.POST.get('remarks', '').strip()
        obj, created = BookingStatus.objects.update_or_create(
            mobile=mobile,
            booking_id=booking_id or None,
            defaults={
                'status': status,
                'driver_name': driver_name,
                'remarks': remarks,
            }
        )
        messages.success(request, "Booking status saved.")
        return redirect('booking_status')
    return render(request, 'booking_status.html', {
        'prefill_mobile': request.session.get('otp_mobile', ''),
    })
