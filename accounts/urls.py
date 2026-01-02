from django.urls import path
from . import views
from .views import Login, register, agency_account, Logout, set_amount

urlpatterns = [
    path('login/', Login, name='login'),
    path('register/', register, name='register'),
    path('logout/', Logout, name='logout'),
    path("agency_accounts/", agency_account, name='agency_accounts'),
    path("password-reset/", views.password_reset_request, name="password_reset_request"),
    path("set_amount/", set_amount, name="set_amount")
]
