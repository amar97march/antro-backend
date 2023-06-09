from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt import views as jwt_views

from .views import *

app_name = 'users'

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('send-otp/', SendOTP.as_view(), name='register'),
    path('verify-otp/', VerifyOTP.as_view(), name='register'),
    path('change-password/', ChangePasswordView.as_view(), name='register'),
    path('token-refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('get_data/<str:id>/', GetData.as_view(), name='get_data'),
]
