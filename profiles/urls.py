from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt import views as jwt_views

from .views import *

app_name = 'profiles'

urlpatterns = [
    path('profiles/', ProfileView.as_view(), name='profile'),
    path('search/', SearchProfileView.as_view(), name='search'),
]
