from django.db import models
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

VEHICLE_TYPES = [
    ('CAR', 'Car'),
    ('TRAVELLER (MINI)', 'Traveller Bus (Mini)'),
    ('TOURIST BUS', 'Tourist Bus'),
    ('LUXURY', 'Luxury Bus'),
]
STATUS = [
    ('Available', 'Available'),
    ('Booked', 'Booked'),
    ('Maintenence', 'maintenence')
]
Licence_Type = [
    ('LMV', 'LMV'),
    ('HMV', 'HMV')
]

class Agency(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agency")
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    agency_name = models.CharField(max_length=100)

    def __str__(self):
        return self.agency_name

class SeatCapacity(models.IntegerChoices):
    SEAT_4 = 4, "4 Seater"
    SEAT_5 = 5, "5 Seater"
    SEAT_7 = 7, "7 Seater"
    SEAT_11 = 11, "11 Seater"
    SEAT_17 = 17, "17 Seater"
    SEAT_25 = 25, "25 Seater"
    SEAT_31 = 31, "31 Seater"
    SEAT_40 = 40, "40 Seater"
    SEAT_ABOVE_50 = 50, "50+ Seater"
    
class Vehicle(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='vehicles', null=True, blank=True)
    v_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    v_seat = models.IntegerField(choices=SeatCapacity.choices)
    v_model = models.CharField(max_length=100)
    v_number = models.CharField(max_length=20, unique=True)
    
    status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0][0])
    v_img = models.ImageField(upload_to='Vehicle_images')
    pollution = models.DateField(null=True, blank=True)
    permit = models.DateField(null=True, blank=True)
    fitness = models.DateField(null=True, blank=True)
    authorize = models.DateField(null=True, blank=True) or None
    insurance = models.DateField(null=True, blank=True)

    authorized_driver = models.ForeignKey('Driver',on_delete=models.SET_NULL,null=True,blank=True,related_name='authorized_vehicles')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.v_model} ({self.get_v_type_display()})"

class Driver(models.Model):
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE, related_name='drivers', null=True, blank=True)

    driver_name = models.CharField(max_length=50)
    driver_img = models.ImageField(upload_to='Driver_images')

    # DOB / AGE (only one will be filled)
    driver_dob = models.DateField(null=True, blank=True)
    driver_age = models.IntegerField(null=True, blank=True)

    driver_phone = models.CharField(max_length=10)
    licence_number = models.CharField(max_length=20)
    licence_type = models.CharField(max_length=10, choices=Licence_Type)
    validity = models.DateField()
    licence_file = models.FileField(upload_to='Licence_files', null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.driver_name} - {self.licence_number}"
    
@receiver(post_delete, sender=Driver)
def delete_driver_image(sender, instance, **kwargs):
    if instance.driver_img:
        instance.driver_img.delete(save=False)

@receiver(post_delete, sender=Vehicle)
def delete_vehicle_image(sender, instance, **kwargs):
    if instance.v_img:
        instance.v_img.delete(save=False)