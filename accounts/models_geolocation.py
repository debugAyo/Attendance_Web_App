"""
IP Geolocation Models for tracking user location data.
Uses free IP-API service for geolocation lookup.
Includes Geofence management for site-based check-in validation.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from math import radians, cos, sin, asin, sqrt


class Geofence(models.Model):
    """
    Geofence model for defining allowed check-in locations/sites.
    Supports construction sites, offices, field locations, or any work site.
    """
    SITE_TYPES = [
        ('office', 'Office/Headquarters'),
        ('branch', 'Branch Location'),
        ('site', 'Work Site'),
        ('field', 'Field Location'),
        ('remote', 'Remote Work Zone'),
        ('event', 'Event Venue'),
        ('warehouse', 'Warehouse/Storage'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200, help_text="Site/Location name")
    description = models.TextField(blank=True, help_text="Additional details about this location")
    site_type = models.CharField(max_length=20, choices=SITE_TYPES, default='office')
    
    # GPS Coordinates (precise location)
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Latitude coordinate (-90 to 90)"
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Longitude coordinate (-180 to 180)"
    )
    
    # Geofence radius in meters
    radius = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(10), MaxValueValidator(10000)],
        help_text="Check-in radius in meters (10-10000m)"
    )
    
    # Address information
    address = models.CharField(max_length=500, blank=True, help_text="Street address")
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True, help_text="Whether this location accepts check-ins")
    require_gps = models.BooleanField(default=True, help_text="Require GPS verification for check-in")
    allow_remote = models.BooleanField(default=False, help_text="Allow check-ins outside geofence")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_geofences'
    )
    
    class Meta:
        verbose_name = "Geofence Location"
        verbose_name_plural = "Geofence Locations"
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active', 'site_type']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_site_type_display()})"
    
    @property
    def coordinates(self):
        """Return coordinates as tuple."""
        return (float(self.latitude), float(self.longitude))
    
    @property
    def full_address(self):
        """Return formatted full address."""
        parts = [p for p in [self.address, self.city, self.state, self.postal_code, self.country] if p]
        return ", ".join(parts) if parts else "No address specified"
    
    def is_within_geofence(self, lat, lng):
        """
        Check if given coordinates are within this geofence.
        Uses Haversine formula for accurate distance calculation.
        """
        if lat is None or lng is None:
            return False
        
        distance = self.calculate_distance(lat, lng)
        return distance <= self.radius
    
    def calculate_distance(self, lat, lng):
        """
        Calculate distance in meters between geofence center and given coordinates.
        Uses Haversine formula for accuracy on Earth's surface.
        """
        # Convert to radians
        lat1, lon1 = radians(float(self.latitude)), radians(float(self.longitude))
        lat2, lon2 = radians(float(lat)), radians(float(lng))
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Earth's radius in meters
        r = 6371000
        
        return c * r


class IPGeolocation(models.Model):
    """
    Store IP geolocation data for tracking login/check-in locations.
    """
    ip_address = models.GenericIPAddressField(db_index=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    region_name = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    isp = models.CharField(max_length=200, blank=True, null=True)
    org = models.CharField(max_length=200, blank=True, null=True)
    as_name = models.CharField(max_length=200, blank=True, null=True)
    is_mobile = models.BooleanField(default=False)
    is_proxy = models.BooleanField(default=False)
    is_hosting = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "IP Geolocation"
        verbose_name_plural = "IP Geolocations"
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['country']),
            models.Index(fields=['city']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.city}, {self.country}"
    
    @property
    def location_display(self):
        """Return a formatted location string."""
        parts = [p for p in [self.city, self.region_name, self.country] if p]
        return ", ".join(parts) if parts else "Unknown"
    
    @property
    def coordinates(self):
        """Return latitude and longitude as a tuple."""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None


class LoginLocation(models.Model):
    """
    Track login locations for users (admins).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_locations')
    geolocation = models.ForeignKey(IPGeolocation, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=True)
    
    # GPS-based exact location (from browser)
    device_latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    device_longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    gps_accuracy = models.FloatField(blank=True, null=True, help_text="GPS accuracy in meters")
    
    class Meta:
        verbose_name = "Login Location"
        verbose_name_plural = "Login Locations"
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', '-login_time']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['-login_time']),
        ]
    
    def __str__(self):
        location = self.geolocation.location_display if self.geolocation else self.ip_address
        return f"{self.user.username} - {location} at {self.login_time}"
    
    @property
    def device_coordinates(self):
        """Return device GPS coordinates as tuple."""
        if self.device_latitude and self.device_longitude:
            return (float(self.device_latitude), float(self.device_longitude))
        return None
    
    @property
    def exact_location_display(self):
        """Return the most precise location available."""
        if self.device_latitude and self.device_longitude:
            return f"GPS: {self.device_latitude}, {self.device_longitude}"
        elif self.geolocation:
            return self.geolocation.location_display
        return self.ip_address


class AttendanceLocation(models.Model):
    """
    Track check-in locations for members/employees.
    Supports GPS-based geofence validation.
    """
    member_phone = models.CharField(max_length=30, db_index=True)
    member_name = models.CharField(max_length=150)
    geolocation = models.ForeignKey(IPGeolocation, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    service_name = models.CharField(max_length=100, blank=True, null=True)
    
    # GPS-based location (from device)
    device_latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    device_longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    gps_accuracy = models.FloatField(blank=True, null=True, help_text="GPS accuracy in meters")
    
    # Geofence validation
    geofence = models.ForeignKey(Geofence, on_delete=models.SET_NULL, null=True, blank=True)
    is_within_geofence = models.BooleanField(default=False)
    distance_from_site = models.FloatField(blank=True, null=True, help_text="Distance from site in meters")
    
    class Meta:
        verbose_name = "Check-in Location"
        verbose_name_plural = "Check-in Locations"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['member_phone', '-timestamp']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['is_within_geofence']),
        ]
    
    def __str__(self):
        location = self.geolocation.location_display if self.geolocation else self.ip_address
        status = "✓" if self.is_within_geofence else "✗"
        return f"{self.member_name} ({self.member_phone}) - {location} [{status}] at {self.timestamp}"
    
    @property
    def device_coordinates(self):
        """Return device GPS coordinates as tuple."""
        if self.device_latitude and self.device_longitude:
            return (float(self.device_latitude), float(self.device_longitude))
        return None
    
    def validate_geofence(self, geofence=None):
        """
        Validate if check-in is within specified geofence.
        Updates is_within_geofence and distance_from_site fields.
        """
        if geofence is None:
            geofence = self.geofence
        
        if geofence and self.device_latitude and self.device_longitude:
            self.distance_from_site = geofence.calculate_distance(
                self.device_latitude, self.device_longitude
            )
            self.is_within_geofence = self.distance_from_site <= geofence.radius
            self.geofence = geofence
        else:
            self.is_within_geofence = False
            self.distance_from_site = None
