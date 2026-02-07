from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
    )
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    HOW_HEARD_CHOICES = (
        ('referral', 'School Referral'),
        ('friend', 'Through a Friend/Family Member'),
        ('social_media', 'Social Media (Facebook, Instagram, etc.)'),
        ('website', 'School Website'),
        ('passing_by', 'Passing By/Open House Visit'),
        ('relocation', 'Relocated to the Area'),
        ('invitation', 'Invited by Student/Staff'),
        ('other', 'Other'),
    )
    # allow null user for members who don't have an auth.User account
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # store member contact info when no auth user exists
    name = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True, db_index=True)  # Add index
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', db_index=True)  # Add index
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True, help_text="Expected graduation year")
    
    # New fields for enhanced features
    first_visit_date = models.DateField(auto_now_add=True, null=True, blank=True)
    is_first_timer = models.BooleanField(default=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    receive_sms = models.BooleanField(default=True, help_text="Receive SMS notifications for events")
    
    # First-timer enquiry
    how_heard = models.CharField(
        max_length=50, 
        choices=HOW_HEARD_CHOICES, 
        null=True, 
        blank=True,
        help_text="How did you hear about our school?"
    )
    how_heard_other = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        help_text="Please specify if 'Other'"
    )

    class Meta:
        indexes = [
            models.Index(fields=['role']),  # Index for role filtering
        ]

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.role}"
        return f"{self.name or 'Unknown'} - {self.role}"
    
    def mark_as_returning_member(self):
        """Mark member as returning (no longer first timer)"""
        if self.is_first_timer:
            self.is_first_timer = False
            self.save()

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} logged in at {self.login_time}'


# Events Models - ChurchEvent kept for DB compatibility, aliased as SchoolEvent
class ChurchEvent(models.Model):
    """Model for school events and activities calendar."""
    
    EVENT_TYPES = [
        ('assembly', 'School Assembly'),
        ('lecture', 'Lecture/Class'),
        ('seminar', 'Seminar/Workshop'),
        ('excursion', 'Excursion/Field Trip'),
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

# Alias for code clarity
SchoolEvent = ChurchEvent


class EventRegistration(models.Model):
    """Track student registration for events."""
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
