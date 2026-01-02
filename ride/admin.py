from django.contrib import admin
from .models import Booking
from .models import BookingStatus

# Register your models here.
admin.site.register(Booking)
class BookingStatusAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'booking_id', 'status', 'driver_name', 'updated_at')
    search_fields = ('mobile', 'booking_id', 'driver_name', 'remarks')