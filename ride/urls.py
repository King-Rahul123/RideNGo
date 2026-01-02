from django.urls import path
from .views import create_booking, booking, status
from . import views

urlpatterns = [
    path('booking', booking, name='booking'),
    path('status', status, name='status'),
    path('book/', create_booking, name='create-booking'),
    path('booking/status/', views.booking_status_view, name='booking_status'),
    path('booking/send-otp/', views.send_otp, name='booking_send_otp'),
    path('booking/verify-otp/', views.verify_otp, name='booking_verify_otp'),
]