from django.db import models
from agency.models import Agency, SeatCapacity, Vehicle
import uuid

def __str__(self):
    # show agency name if available, else vehicle model, else id
    provider = self.agency.agency_name if self.agency else (self.vehicle.v_model if self.vehicle else "Booking")
    return f"{self.v_type} - {provider} ({self.booking_from} to {self.booking_to})"

VEHICLE_TYPES = [
    ('CAR', 'Car'),
    ('TRAVELLER_MINI', 'Traveller Bus (Mini)'),
    ('TOURIST_BUS', 'Tourist Bus'),
    ('LUXURY', 'Luxury Bus'),
]

STATUS = [
    ('Available', 'Available'),
    ('Booked', 'Booked'),
    ('Maintenence', 'maintenence')
]

class Booking(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')

    v_type = models.CharField(max_length=30, choices=VEHICLE_TYPES)
    v_seat = models.IntegerField(choices=SeatCapacity.choices)
    v_model = models.CharField(max_length=255, blank=True, null=True)      # vehicle model

    pickup_address = models.TextField()
    destination = models.CharField(max_length=255)

    # Booking details
    booking_from = models.DateField()
    booking_to = models.DateField()
    pickup_time = models.TimeField()
    purpose = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.v_type} - {self.v_provider} ({self.booking_from} to {self.booking_to})"


class BookingStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mobile = models.CharField(max_length=20, db_index=True)
    booking_id = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=64, default='pending')
    driver_name = models.CharField(max_length=120, blank=True)
    remarks = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mobile} - {self.booking_id or 'no-id'} - {self.status}"
