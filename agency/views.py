# from email import message
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Driver, Vehicle, Agency
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required(login_url='login')
def dashboard_home(request):
    agency = getattr(request.user, "agency", None)

    if agency:
        total_vehicles = Vehicle.objects.filter(agency=agency).count()
    else:
        total_vehicles = 0
        
    return render(request, 'dashboard_home.html', {'total_vehicles': total_vehicles})

@login_required(login_url='login')
def vehicles(request):
    agency = getattr(request.user, "agency", None)

    # 2) If no OneToOne relation, try to find Agency by user FK (fallback)
    if not agency:
        agency = Agency.objects.filter(user=request.user).first()
        messages.info(request, "You don't have an agency profile yet.")
        vehicle_qs = Vehicle.objects.none()
    else:
        # Correct filtering: pass an Agency instance OR use agency__user=request.user
        vehicle_qs = Vehicle.objects.filter(agency=agency).order_by('-created_at')

        drivers = Driver.objects.filter(agency=agency)

    return render(request, 'vehicles.html', {'vehicles': vehicle_qs,'drivers': drivers})

@login_required(login_url='login')
def my_vehicles_view(request):
    agency = getattr(request.user, "agency", None)
    if not agency:
        messages.info(request, "You don't have an agency profile yet.")
        vehicles = Vehicle.objects.none()
    else:
        try:
            vehicles = agency.vehicles.all()
        except Exception:
            vehicles = Vehicle.objects.filter(agency=agency)

    return render(request, 'vehicles.html', {'vehicles': vehicles})

@login_required(login_url='login')
def add_vehicles(request):
    # Ensure the user has an agency
    agency = getattr(request.user, "agency", None)
    if not agency:
        messages.error(request, "You need an agency profile before adding vehicles.")
        return redirect('agency:create_agency')  # adjust to your create-agency url name

    if request.method == 'POST':
        # Gather fields from POST/FILES
        v_type = request.POST.get('v_type', '').strip()
        v_seat = request.POST.get('seats', '').strip()
        v_model = request.POST.get('v_model', '').strip()
        v_number = request.POST.get('v_number', '').strip()
        status = request.POST.get('status') or Vehicle._meta.get_field('status').get_default()
        v_img = request.FILES.get('v_img')              # file from request.FILES
        pollution = request.POST.get('pollution', '').strip() or None
        permit = request.POST.get('permit', '').strip() or None
        fitness = request.POST.get('fitness', '').strip() or None
        authorize = request.POST.get('authorize', '').strip() or None
        insurance = request.POST.get('insurance', '').strip() or None

        # Basic validation: require the minimal fields
        if not (v_type and v_seat and v_model and v_number and v_img):
            messages.error(request, "Please fill out all required fields ...")
            return redirect('vehicles')

        # Prevent duplicate registration number
        if Vehicle.objects.filter(v_number=v_number).exists():
            messages.error(request, "Vehicle already exists.")
            return redirect('vehicles')

        try:
            vehicle = Vehicle (
                agency=agency,
                v_type=v_type,
                v_seat=v_seat,
                v_model=v_model,
                v_number=v_number,
                status=status,
                v_img=v_img,
                pollution=pollution,
                permit=permit,
                fitness=fitness,
                authorize=authorize,
                insurance=insurance,
            )
            vehicle.save()
            messages.success(request, "Vehicle added successfully!")
            return redirect('vehicles')
        except IntegrityError:
            messages.error(request, "Database error while saving vehicle. Possibly duplicate unique field.")
            return redirect('vehicles')
        except TypeError as e:
            # Catch unexpected keyword args or type mistakes
            messages.error(request, f"Server error: {e}")
            return redirect('vehicles')

    return redirect('vehicles')

@login_required(login_url='login')
def bookings(request):
    return render(request, 'bookings.html')

@login_required(login_url='login')
def add_drivers(request):
    # Ensure the user has an agency
    agency = getattr(request.user, "agency", None)
    if not agency:
        messages.error(request, "You need an agency profile before adding driver.")
        return redirect('agency:create_agency')  # adjust to your create-agency url name

    if request.method == 'POST':
        # Gather fields from POST/FILES
        driver_name = request.POST.get('driver_name', '').strip()
        driver_phone = request.POST.get('driver_phone', '').strip()
        licence_number = request.POST.get('licence_number', '').strip()
        driver_dob = request.POST.get('driver_dob', '').strip() or None
        driver_age = request.POST.get('driver_age', '').strip() or None
        driver_img = request.FILES.get('driver_img')              # file from request.FILES
        licence_type = request.POST.get('licence_type', '').strip()
        validity = request.POST.get('validity', '').strip()
        licence_file = request.FILES.get('licence_file', '').strip() or None
        notes = request.POST.get('notes', '').strip() or None

        # Basic validation: require the minimal fields
        if not (driver_name and licence_number and driver_phone and licence_type and driver_img):
            messages.error(request, "Please fill out all required fields ...")
            return redirect('driver')

        # Prevent duplicate registration number
        if Driver.objects.filter(licence_number = licence_number).exists():
            messages.error(request, "Driver already exists.")
            return redirect('driver')

        try:
            driver = Driver (
                agency=agency,
                driver_name = driver_name,
                driver_phone = driver_phone,
                driver_img = driver_img,
                driver_dob = driver_dob,
                driver_age = driver_age,
                licence_type = licence_type,
                licence_number = licence_number,
                licence_file = licence_file,
                validity = validity,
                notes = notes
            )
            driver.save()
            messages.success(request, "Driver added successfully!")
            return redirect('driver')
        except IntegrityError:
            messages.error(request, "Database error while saving driver. Possibly duplicate unique field.")
            return redirect('driver')
        except TypeError as e:
            # Catch unexpected keyword args or type mistakes
            messages.error(request, f"Server error: {e}")
            return redirect('driver')
    return redirect('driver')

@login_required(login_url='login')
def driver(request):
    agency = getattr(request.user, "agency", None)

    if not agency:
        messages.info(request, "You don't have an agency profile yet.")
        driver = Driver.objects.none()
    else:
        driver = Driver.objects.filter(agency=agency).order_by('-id')

    return render(request, 'drivers.html', {'driver': driver})

@login_required(login_url='login')
def update_vehicle(request, pk):
    if request.method == "POST":
        agency = getattr(request.user, "agency", None)
        vehicle = get_object_or_404(Vehicle, pk=pk, agency=agency)

        # ✅ Update ONLY if value is provided
        status = request.POST.get('status')
        if status:
            vehicle.status = status

        pollution = request.POST.get('pollution')
        if pollution:
            vehicle.pollution = pollution

        fitness = request.POST.get('fitness')
        if fitness:
            vehicle.fitness = fitness

        insurance = request.POST.get('insurance')
        if insurance:
            vehicle.insurance = insurance

        permit = request.POST.get('permit')
        if permit:
            vehicle.permit = permit

        # 🔥 FIXED LOGIC HERE
        driver_id = request.POST.get('authorized_driver')
        authorize = request.POST.get('authorize')

        if driver_id in [None, 'None']:
            vehicle.authorized_driver = None
            vehicle.authorize = None
        else:
            authorize = request.POST.get('authorize')
            if authorize:
                vehicle.authorize = authorize

            # ✅ Driver update ONLY if selected
            driver_id = request.POST.get('authorized_driver')
            if driver_id:
                vehicle.authorized_driver = get_object_or_404(
                    Driver, id=driver_id, agency=agency
                )
            # else → keep existing driver (DO NOTHING)

        # ✅ Image update ONLY if new image uploaded
        if request.FILES.get('v_img'):
            vehicle.v_img = request.FILES['v_img']

        vehicle.save()
        messages.success(request, "Vehicle updated successfully.")
        return redirect('vehicles')

    return redirect('vehicles')

def delete_vehicle(request, pk):
    agency = getattr(request.user, "agency", None)
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if not agency or vehicle.agency_id != agency.id:
        return JsonResponse({'ok': False, 'message': 'Permission denied.'}, status=403)

    try:
        vehicle.delete()
        return JsonResponse({'ok': True, 'message': 'Vehicle deleted', 'id': pk})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': f'Error deleting vehicle: {e}'}, status=500)
    
@login_required(login_url='login')
def delete_driver(request, pk):
    if request.method != "POST":
        return JsonResponse({'ok': False, 'message': 'Invalid request'}, status=400)

    agency = getattr(request.user, "agency", None)
    driver = get_object_or_404(Driver, pk=pk)

    if not agency or driver.agency_id != agency.id:
        return JsonResponse({'ok': False, 'message': 'Permission denied'}, status=403)

    try:
        driver.delete()
        return JsonResponse({'ok': True, 'id': pk})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)}, status=500)
