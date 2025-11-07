from django.db import models
from django.utils import timezone


class ChurchEvent(models.Model):
    """Model for church events and activities calendar."""
    
    EVENT_TYPES = [
        ('service', 'Church Service'),
        ('prayer', 'Prayer Meeting'),
        ('fellowship', 'Fellowship'),
        ('outreach', 'Outreach'),
        ('training', 'Training/Workshop'),
        ('celebration', 'Celebration'),
        ('conference', 'Conference'),
        ('meeting', 'Meeting'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='service')
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    organizer = models.CharField(max_length=100, blank=True)
    is_recurring = models.BooleanField(default=False)
    recurring_pattern = models.CharField(
        max_length=50, 
        blank=True,
        help_text="e.g., 'Weekly on Sunday', 'Monthly first Saturday'"
    )
    max_attendees = models.IntegerField(blank=True, null=True, help_text="Leave blank for unlimited")
    registration_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date', 'start_time']
        indexes = [
            models.Index(fields=['start_date', 'is_active']),
            models.Index(fields=['event_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_date}"
    
    @property
    def is_upcoming(self):
        """Check if event is in the future."""
        from datetime import date
        return self.start_date >= date.today()
    
    @property
    def is_today(self):
        """Check if event is happening today."""
        from datetime import date
        return self.start_date == date.today()
    
    @property
    def duration_days(self):
        """Calculate event duration in days."""
        if self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 1


class EventRegistration(models.Model):
    """Track member registration for events."""
    event = models.ForeignKey(ChurchEvent, on_delete=models.CASCADE, related_name='registrations')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['event', 'phone']
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.name} - {self.event.title}"
