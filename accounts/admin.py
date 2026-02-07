from django.contrib import admin
from .models import Profile, UserActivity, ChurchEvent, EventRegistration
from .models_geolocation import IPGeolocation, LoginLocation, AttendanceLocation


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


# IP Geolocation Models
@admin.register(IPGeolocation)
class IPGeolocationAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'city', 'country', 'isp', 'is_mobile', 'is_proxy', 'last_updated']
    list_filter = ['country', 'is_mobile', 'is_proxy', 'is_hosting']
    search_fields = ['ip_address', 'city', 'country', 'isp']
    readonly_fields = ['last_updated']
    ordering = ['-last_updated']


@admin.register(LoginLocation)
class LoginLocationAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'get_location', 'login_time', 'is_successful']
    list_filter = ['is_successful', 'login_time', 'geolocation__country']
    search_fields = ['user__username', 'ip_address', 'geolocation__city']
    date_hierarchy = 'login_time'
    ordering = ['-login_time']
    
    def get_location(self, obj):
        if obj.geolocation:
            return obj.geolocation.location_display
        return "Local/Private IP"
    get_location.short_description = 'Location'


@admin.register(AttendanceLocation)
class AttendanceLocationAdmin(admin.ModelAdmin):
    list_display = ['member_name', 'member_phone', 'service_name', 'get_location', 'timestamp']
    list_filter = ['timestamp', 'geolocation__country', 'service_name']
    search_fields = ['member_name', 'member_phone', 'ip_address', 'geolocation__city']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def get_location(self, obj):
        if obj.geolocation:
            return obj.geolocation.location_display
        return "Local/Private IP"
    get_location.short_description = 'Location'
