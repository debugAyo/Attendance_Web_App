"""
IP Geolocation Service - Utility functions for fetching and storing IP location data.
Uses the free ip-api.com service (45 requests per minute limit).
"""
import logging
import requests
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

# IP-API endpoint (free, no API key required)
IP_API_URL = "http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting"

# Cache timeout (24 hours) - IP locations don't change frequently
CACHE_TIMEOUT = 86400


def get_client_ip(request):
    """
    Extract the real client IP address from the request.
    Handles various proxy headers (X-Forwarded-For, X-Real-IP, etc.)
    """
    # Check for forwarded IP headers (in order of reliability)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs, the first one is the client
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip.strip()
    
    # Fall back to REMOTE_ADDR
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def get_user_agent(request):
    """Extract user agent from request."""
    return request.META.get('HTTP_USER_AGENT', '')


def is_private_ip(ip):
    """
    Check if an IP address is private/local (not routable on the internet).
    These IPs cannot be geolocated.
    """
    if not ip:
        return True
    
    # Handle IPv4 private ranges
    if ip.startswith('10.') or ip.startswith('192.168.'):
        return True
    if ip.startswith('172.'):
        # Check 172.16.0.0 - 172.31.255.255
        try:
            second_octet = int(ip.split('.')[1])
            if 16 <= second_octet <= 31:
                return True
        except (IndexError, ValueError):
            pass
    
    # Localhost
    if ip in ('127.0.0.1', '::1', 'localhost'):
        return True
    
    # Link-local
    if ip.startswith('169.254.'):
        return True
    
    return False


def fetch_geolocation(ip_address):
    """
    Fetch geolocation data from IP-API service.
    Returns a dictionary with location data or None if failed.
    """
    if is_private_ip(ip_address):
        logger.debug(f"Skipping geolocation for private IP: {ip_address}")
        return None
    
    # Check cache first
    cache_key = f"geolocation_{ip_address}"
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.debug(f"Using cached geolocation for IP: {ip_address}")
        return cached_data
    
    try:
        response = requests.get(
            IP_API_URL.format(ip=ip_address),
            timeout=5  # 5 second timeout
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'success':
            geo_data = {
                'country': data.get('country'),
                'country_code': data.get('countryCode'),
                'region': data.get('region'),
                'region_name': data.get('regionName'),
                'city': data.get('city'),
                'zip_code': data.get('zip'),
                'latitude': data.get('lat'),
                'longitude': data.get('lon'),
                'timezone': data.get('timezone'),
                'isp': data.get('isp'),
                'org': data.get('org'),
                'as_name': data.get('as'),
                'is_mobile': data.get('mobile', False),
                'is_proxy': data.get('proxy', False),
                'is_hosting': data.get('hosting', False),
            }
            
            # Cache the result
            cache.set(cache_key, geo_data, CACHE_TIMEOUT)
            logger.info(f"Fetched geolocation for IP {ip_address}: {geo_data.get('city')}, {geo_data.get('country')}")
            return geo_data
        else:
            logger.warning(f"IP-API failed for {ip_address}: {data.get('message')}")
            return None
            
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout fetching geolocation for IP: {ip_address}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching geolocation for IP {ip_address}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in geolocation fetch for {ip_address}: {e}")
        return None


def get_or_create_geolocation(ip_address):
    """
    Get or create an IPGeolocation record for the given IP address.
    Returns the IPGeolocation instance or None if geolocation failed.
    """
    from .models_geolocation import IPGeolocation
    
    if is_private_ip(ip_address):
        return None
    
    # Check if we already have this IP in the database (updated within last 24 hours)
    try:
        recent_threshold = timezone.now() - timedelta(hours=24)
        existing = IPGeolocation.objects.filter(
            ip_address=ip_address,
            last_updated__gte=recent_threshold
        ).first()
        
        if existing:
            return existing
    except Exception as e:
        logger.error(f"Error checking existing geolocation: {e}")
    
    # Fetch fresh geolocation data
    geo_data = fetch_geolocation(ip_address)
    
    if not geo_data:
        return None
    
    try:
        # Update or create the geolocation record
        geolocation, created = IPGeolocation.objects.update_or_create(
            ip_address=ip_address,
            defaults=geo_data
        )
        
        if created:
            logger.info(f"Created new geolocation record for IP: {ip_address}")
        else:
            logger.debug(f"Updated geolocation record for IP: {ip_address}")
        
        return geolocation
        
    except Exception as e:
        logger.error(f"Error saving geolocation for IP {ip_address}: {e}")
        return None


def track_login_location(user, request, is_successful=True):
    """
    Track a user's login location.
    Call this after successful login.
    """
    from .models_geolocation import LoginLocation
    
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    try:
        # Get or create geolocation data
        geolocation = get_or_create_geolocation(ip_address)
        
        # Create login location record
        login_location = LoginLocation.objects.create(
            user=user,
            geolocation=geolocation,
            ip_address=ip_address,
            user_agent=user_agent,
            is_successful=is_successful
        )
        
        location_str = geolocation.location_display if geolocation else ip_address
        logger.info(f"Tracked login for {user.username} from {location_str}")
        
        return login_location
        
    except Exception as e:
        logger.error(f"Error tracking login location for {user.username}: {e}")
        return None


def track_attendance_location(member_phone, member_name, request, service_name=None, 
                              device_latitude=None, device_longitude=None, gps_accuracy=None):
    """
    Track a member's attendance marking location.
    Call this when attendance is marked.
    
    Args:
        member_phone: Member's phone number
        member_name: Member's name
        request: HTTP request object
        service_name: Name of the service/session
        device_latitude: GPS latitude from device (primary location source)
        device_longitude: GPS longitude from device (primary location source)
        gps_accuracy: GPS accuracy in meters
    """
    from .models_geolocation import AttendanceLocation, Geofence
    
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    try:
        # Get or create IP geolocation data (fallback)
        geolocation = get_or_create_geolocation(ip_address)
        
        # Create attendance location record with GPS as primary
        attendance_location = AttendanceLocation.objects.create(
            member_phone=member_phone,
            member_name=member_name,
            geolocation=geolocation,
            ip_address=ip_address,
            user_agent=user_agent,
            service_name=service_name,
            device_latitude=device_latitude,
            device_longitude=device_longitude,
            gps_accuracy=gps_accuracy
        )
        
        # Validate against active geofences if GPS is available
        if device_latitude and device_longitude:
            active_geofences = Geofence.objects.filter(is_active=True)
            for geofence in active_geofences:
                distance = geofence.calculate_distance(device_latitude, device_longitude)
                if distance <= geofence.radius:
                    attendance_location.geofence = geofence
                    attendance_location.is_within_geofence = True
                    attendance_location.distance_from_site = distance
                    attendance_location.save()
                    logger.info(f"GPS check-in within geofence '{geofence.name}' for {member_name}")
                    break
            else:
                # Not within any geofence
                if active_geofences.exists():
                    # Find closest geofence
                    closest = min(active_geofences, key=lambda g: g.calculate_distance(device_latitude, device_longitude))
                    attendance_location.geofence = closest
                    attendance_location.distance_from_site = closest.calculate_distance(device_latitude, device_longitude)
                    attendance_location.is_within_geofence = False
                    attendance_location.save()
        
        # Log location info
        if device_latitude and device_longitude:
            logger.info(f"GPS attendance for {member_name}: ({device_latitude}, {device_longitude}) accuracy: {gps_accuracy}m")
        else:
            location_str = geolocation.location_display if geolocation else ip_address
            logger.info(f"IP-based attendance for {member_name} from {location_str} (no GPS)")
        
        return attendance_location
        
    except Exception as e:
        logger.error(f"Error tracking attendance location for {member_name}: {e}")
        return None


def get_location_stats():
    """
    Get statistics about login and attendance locations.
    Useful for dashboard analytics.
    """
    from .models_geolocation import LoginLocation, AttendanceLocation
    from django.db.models import Count
    from datetime import date, timedelta
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        # Login stats
        'total_logins': LoginLocation.objects.count(),
        'logins_today': LoginLocation.objects.filter(login_time__date=today).count(),
        'logins_this_week': LoginLocation.objects.filter(login_time__date__gte=week_ago).count(),
        'logins_this_month': LoginLocation.objects.filter(login_time__date__gte=month_ago).count(),
        
        # Attendance location stats
        'total_attendance_locations': AttendanceLocation.objects.count(),
        'attendance_today': AttendanceLocation.objects.filter(timestamp__date=today).count(),
        'attendance_this_week': AttendanceLocation.objects.filter(timestamp__date__gte=week_ago).count(),
        
        # Top locations by login
        'top_login_countries': LoginLocation.objects.filter(
            geolocation__isnull=False
        ).values('geolocation__country').annotate(
            count=Count('id')
        ).order_by('-count')[:5],
        
        'top_login_cities': LoginLocation.objects.filter(
            geolocation__isnull=False
        ).values('geolocation__city', 'geolocation__country').annotate(
            count=Count('id')
        ).order_by('-count')[:10],
        
        # Top locations by attendance
        'top_attendance_countries': AttendanceLocation.objects.filter(
            geolocation__isnull=False
        ).values('geolocation__country').annotate(
            count=Count('id')
        ).order_by('-count')[:5],
        
        'top_attendance_cities': AttendanceLocation.objects.filter(
            geolocation__isnull=False
        ).values('geolocation__city', 'geolocation__country').annotate(
            count=Count('id')
        ).order_by('-count')[:10],
        
        # Suspicious activity (proxy/hosting IPs)
        'proxy_logins': LoginLocation.objects.filter(
            geolocation__is_proxy=True
        ).count(),
        
        'mobile_attendance': AttendanceLocation.objects.filter(
            geolocation__is_mobile=True
        ).count(),
    }
    
    return stats
