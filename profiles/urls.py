from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt import views as jwt_views

from .views import *

app_name = 'profiles'

urlpatterns = [
    path('profiles/', ProfileView.as_view(), name='profile'),
    path('search/', SearchProfileView.as_view(), name='search'),
    path('my_profiles/', MyProfilesView.as_view(), name='my_profiles'),
    path('similar_profiles/<int:id>/', SimilarProfilesView.as_view(), name='similar_profiles'),
    path('get_profile_qr/<int:id>/', ProfileQR.as_view(), name="profile_qr"),
    path('get_profile/<str:id>/', ProfileData.as_view(), name="profile_data"),
    path('set_active_profile/<int:profile_id>/', SetActiveProfile.as_view(), name='set_active_profile'),
    path('save_profile/', SaveProfile.as_view(), name='save_profile'),
    path('unsave_profile/', UnsaveProfile.as_view(), name='unsave_profile'),
    path('get_saved_profiles/', GetSavedProfiles.as_view(), name='get_saved_profiles'),
    path('update_profile_picture/', AddProfilePicture.as_view(), name="update_profile_pic"),
    path('profile-categories/', ProfileCategoryListAPIView.as_view(), name='profile-category-list-api'),
    path('profile-category-social-sities/<int:category_id>/', ProfileCategorySocialSiteListAPIView.as_view(), name='profile-category-social-site-list-api')
]
