from django.db import models
from django.contrib.auth.models import User

# ChurchService - keeping original name to match database table
# Can be referred to as SchoolClass in code for clarity
class ChurchService(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, help_text="Unique code for students to mark attendance.")
    members = models.ManyToManyField(User, related_name='school_classes', blank=True)

    def __str__(self):
        return self.name

# Alias for code clarity
SchoolClass = ChurchService

class Attendance(models.Model):
    service = models.ForeignKey(ChurchService, on_delete=models.CASCADE)
    date = models.DateField()
    attendees = models.ManyToManyField(User, related_name='attended_services', blank=True)

    class Meta:
        unique_together = ('service', 'date')

    def __str__(self):
        return f'Attendance for {self.service.name} on {self.date}'

# For members without User accounts
class MemberAttendance(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, db_index=True)  # Add index for faster queries
    service = models.ForeignKey(ChurchService, on_delete=models.CASCADE)
    service_code = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)  # Add index for date queries

    class Meta:
        indexes = [
            models.Index(fields=['phone', 'timestamp']),  # Composite index for common queries
            models.Index(fields=['timestamp']),  # Index for date filtering
        ]

    def __str__(self):
        return f"{self.name} ({self.phone}) - {self.service.name} [{self.service_code}] at {self.timestamp}"
