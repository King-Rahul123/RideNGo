from django.contrib import admin
from django.urls import path, include
from .views import home, pictures
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('pictures/', pictures, name='pictures'),
    path('ride/', include('ride.urls'), name='ride'),
    path('accounts/', include('accounts.urls'), name='accounts'),
    path('agency/', include('agency.urls'), name='agency'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

