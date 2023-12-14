from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt import views as jwt_views

from .views import *

app_name = 'profiles'

urlpatterns = [
    path('calendarevents/', CalendarEventListCreateView.as_view(), name='calendar-event-list-create'),
    path('calendarevents/<int:pk>/', CalendarEventDetailView.as_view(), name='calendar-event-detail'),
]
