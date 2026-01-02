from django.db import models
import uuid
from agency.models import Vehicle


class SetAmount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Each vehicle has one pricing config
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='set_amount')
    manual_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,help_text="Manual price set after booking or default base price")
    is_fixed = models.BooleanField(default=False,help_text="True → Fixed pricing applied; False → Manual pricing only")
    min_km = models.PositiveIntegerField(default=0,help_text="Minimum KM allowed for fixed amount per km",blank=True)
    amount_per_km = models.DecimalField(max_digits=10,decimal_places=2,default=0,blank=True)
    night_charge = models.DecimalField(max_digits=10,decimal_places=2,default=0,blank=True)
    note = models.CharField(max_length=250,blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pricing for {self.vehicle.v_model} ({self.vehicle.v_number})"
