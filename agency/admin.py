from django.contrib import admin
from .models import Agency, Driver, Vehicle

admin.site.register(Agency)
admin.site.register(Vehicle)
admin.site.register(Driver)