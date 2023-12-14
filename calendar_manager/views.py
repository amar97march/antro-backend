# views.py
from rest_framework import generics
from .models import CalendarEvent
from .serializers import CalendarEventSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

class CalendarEventListCreateView(generics.ListCreateAPIView):
    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CalendarEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer
