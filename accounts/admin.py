from django.contrib import admin
from .models import Profile, UserActivity, ChurchEvent, EventRegistration


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'role', 'phone', 'gender']
    list_filter = ['role', 'gender']
    search_fields = ['user__username', 'name', 'phone']


@admin.register(ChurchEvent)
class ChurchEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'start_time', 'location', 'is_active', 'registration_required']
    list_filter = ['event_type', 'is_active', 'registration_required', 'start_date']
    search_fields = ['title', 'description', 'location', 'organizer']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'event', 'registered_at', 'attended']
    list_filter = ['attended', 'event']
    search_fields = ['name', 'phone', 'email']
    date_hierarchy = 'registered_at'
