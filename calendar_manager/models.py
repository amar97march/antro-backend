from django.db import models
from users.models import User

class CalendarEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    other_users = models.ManyToManyField(User, related_name='other_users', blank=True)
    event_type_choices = [
        ('call', 'Call'),
        ('email', 'Email'),
        ('video', 'Video'),
    ]
    event_type = models.CharField(max_length=20, choices=event_type_choices)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField()

    # Additional Fields
    location = models.CharField(max_length=255, blank=True, null=True)
    reminder_time = models.DateTimeField(blank=True, null=True)
    is_all_day = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern_choices = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        # Add more recurrence pattern choices as needed
    ]
    recurrence_pattern = models.CharField(
        max_length=20,
        choices=recurrence_pattern_choices,
        blank=True,
        null=True
    )
    color = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email}'s {self.get_event_type_display()} Event"