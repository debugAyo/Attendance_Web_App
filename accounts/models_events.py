# This file re-exports event models from accounts.models for backward compatibility
# The actual model definitions are in accounts/models.py

from .models import ChurchEvent, EventRegistration

# Alias for school-friendly naming
SchoolEvent = ChurchEvent
