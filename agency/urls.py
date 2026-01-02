from django.urls import path
from .views import dashboard, dashboard_home, vehicles, driver, bookings, add_vehicles, add_drivers, update_vehicle, delete_vehicle, delete_driver
# from . import views

urlpatterns = [
    path('dashboard', dashboard, name='dashboard'),
    path('dashboard_home/', dashboard_home, name='dashboard_home'),
    path('vehicles/', vehicles, name='vehicles'),
    path('vehicles/add/', add_vehicles, name='add_vehicles'),
    path('bookings/', bookings, name='bookings'),
    path('driver/', driver, name='driver'),
    path('driver/add/', add_drivers, name='add_drivers'),
    path('vehicles/<int:pk>/update/', update_vehicle, name='update-vehicle'),
    path('vehicles/<int:pk>/delete/', delete_vehicle, name='delete-vehicle'),
    path('driver/<int:pk>/delete/', delete_driver, name='driver-delete'),

]
