from django.shortcuts import render, redirect, get_object_or_404
from attendance.models import MemberAttendance, ChurchService, SchoolClass
from accounts.models import Profile
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count
from django.db import models
from datetime import datetime, timedelta, date
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from functools import wraps
import csv
import json


# ==================== SECURITY DECORATORS ====================

def admin_required(view_func):
    """
    Decorator that checks if user is logged in AND is an admin (staff/superuser or has admin profile).
    Redirects to login page if not authenticated.
    Shows 403 Forbidden if authenticated but not admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        # Check if user is admin
        is_admin = (
            request.user.is_superuser or 
            request.user.is_staff or
            Profile.objects.filter(user=request.user, role='admin').exists()
        )
        
        if not is_admin:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden(
                '<h1>403 Forbidden</h1><p>You do not have permission to access this page.</p>'
                '<p><a href="/">Go to Home</a></p>'
            )
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ==================== ADMIN VIEWS ====================

@admin_required
def admin_manage_members(request):
    # Get all member profiles (user=None) - optimized query
    members = Profile.objects.filter(role='member').only(
        'id', 'name', 'phone', 'gender', 'date_of_birth', 'email', 'first_visit_date'
    )
    member_data = []
    
    # Bulk count attendance for all members to avoid N+1 queries
    member_phones = [m.phone for m in members]
    attendance_counts = {}
    if member_phones:
        from django.db.models import Count
        attendance_data = MemberAttendance.objects.filter(
            phone__in=member_phones
        ).values('phone').annotate(count=Count('id'))
        attendance_counts = {item['phone']: item['count'] for item in attendance_data}
    
    # Calculate age for each member
    from datetime import date
    today = date.today()
    
    for m in members:
        age = None
        if m.date_of_birth:
            age = today.year - m.date_of_birth.year - (
                (today.month, today.day) < (m.date_of_birth.month, m.date_of_birth.day)
            )
        
        member_data.append({
            'id': m.id,
            'name': m.name,
            'phone': m.phone,
            'gender': m.gender,
            'date_of_birth': m.date_of_birth,
            'age': age,
            'email': m.email,
            'first_visit_date': m.first_visit_date,
            'attendance_count': attendance_counts.get(m.phone, 0),
        })
    
    # Export CSV if requested
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="members.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Phone', 'Gender', 'Date of Birth', 'Age', 'Email', 'First Visit', 'Attendance Count'])
        for m in member_data:
            writer.writerow([
                m['name'], m['phone'], m['gender'], m['date_of_birth'], 
                m['age'], m['email'], m['first_visit_date'], m['attendance_count']
            ])
        return response
    return render(request, 'admin_manage_members.html', {'members': member_data})

@admin_required
def remove_member(request, member_id):
    member = get_object_or_404(Profile, id=member_id, role='member')
    member.delete()
    return redirect('admin_manage_members')

@admin_required
def edit_member(request, member_id):
    member = get_object_or_404(Profile, id=member_id, role='member')
    if request.method == 'POST':
        member.name = request.POST.get('name')
        member.phone = request.POST.get('phone')
        member.gender = request.POST.get('gender')
        
        # Handle date of birth
        dob = request.POST.get('date_of_birth')
        if dob:
            member.date_of_birth = dob
        else:
            member.date_of_birth = None
        
        # Handle email
        email = request.POST.get('email')
        if email:
            member.email = email
        else:
            member.email = None
        
        member.save()
        messages.success(request, f'Member {member.name} updated successfully.')
        return redirect('admin_manage_members')
    
    return render(request, 'edit_member.html', {'member': member})

@admin_required
def admin_todays_attendance(request):
    today = date.today()
    todays_attendance = MemberAttendance.objects.filter(timestamp__date=today).select_related('service')
    
    # Group attendance by service
    service_stats = MemberAttendance.objects.filter(
        timestamp__date=today
    ).values('service__name', 'service_code').annotate(
        total=Count('id')
    ).order_by('service__name')
    
    # Export CSV if requested
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_{today}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Phone', 'Service', 'Code', 'Time'])
        for a in todays_attendance:
            writer.writerow([a.name, a.phone, a.service.name, a.service_code, a.timestamp.strftime('%I:%M %p')])
        return response
    
    return render(request, 'admin_todays_attendance.html', {
        'todays_attendance': todays_attendance,
        'service_stats': service_stats
    })

@admin_required
def remove_attendance(request, attendance_id):
    attendance = get_object_or_404(MemberAttendance, id=attendance_id)
    attendance.delete()
    return redirect('admin_todays_attendance')

@admin_required
def admin_summary(request):
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Optimized queries - use only() to fetch only needed fields
    total_members = Profile.objects.filter(role='member').count()
    present_today = MemberAttendance.objects.filter(timestamp__date=today).count()
    this_week = MemberAttendance.objects.filter(timestamp__date__gte=week_ago).count()
    this_month = MemberAttendance.objects.filter(timestamp__date__gte=month_ago).count()
    
    # First-timers this week
    first_timers_week = Profile.objects.filter(
        role='member',
        is_first_timer=True,
        first_visit_date__gte=week_ago
    ).count()
    
    # Upcoming birthdays (next 30 days)
    upcoming_birthdays = []
    members_with_dob = Profile.objects.filter(
        role='member',
        date_of_birth__isnull=False
    ).only('name', 'phone', 'date_of_birth')
    
    for member in members_with_dob:
        # Calculate next birthday
        next_birthday = member.date_of_birth.replace(year=today.year)
        if next_birthday < today:
            next_birthday = member.date_of_birth.replace(year=today.year + 1)
        
        days_until = (next_birthday - today).days
        if 0 <= days_until <= 30:
            upcoming_birthdays.append({
                'name': member.name,
                'phone': member.phone,
                'date': next_birthday,
                'days_until': days_until
            })
    
    upcoming_birthdays.sort(key=lambda x: x['days_until'])
    
    # Top attendees - optimized with values and annotate
    top_attendees = MemberAttendance.objects.values('name', 'phone').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Chart data (last 7 days) - single query per day
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        chart_labels.append(day.strftime('%a'))
        count = MemberAttendance.objects.filter(timestamp__date=day).count()
        chart_data.append(count)
    
    context = {
        'total_members': total_members,
        'present_today': present_today,
        'this_week': this_week,
        'this_month': this_month,
        'first_timers_week': first_timers_week,
        'upcoming_birthdays': upcoming_birthdays[:5],  # Show only top 5
        'top_attendees': top_attendees,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'admin_summary.html', context)

@admin_required
def admin_settings(request):
    # Optimized queries - only fetch needed fields
    services = SchoolClass.objects.all().only('id', 'name', 'code')
    
    # Only show admin management to superusers
    admins = None
    if request.user.is_superuser:
        # Get all superusers
        superusers = User.objects.filter(is_superuser=True)
        
        # Get users with admin profile (safely handle missing profiles)
        try:
            admin_profiles = User.objects.filter(
                profile__role='admin'
            ).select_related('profile')
        except:
            admin_profiles = User.objects.none()
        
        # Combine both querysets
        admins = (superusers | admin_profiles).distinct().only('id', 'username', 'email', 'is_superuser')
    
    return render(request, 'admin_settings.html', {
        'services': services, 
        'admins': admins, 
        'is_superuser': request.user.is_superuser
    })

@admin_required
def add_service(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        
        # Check if service code already exists
        if SchoolClass.objects.filter(code=code).exists():
            messages.error(request, f'A class with code "{code}" already exists. Please use a unique code.')
            return render(request, 'add_service.html', {'name': name, 'code': code})
        
        try:
            SchoolClass.objects.create(name=name, code=code)
            messages.success(request, f'Service "{name}" with code "{code}" created successfully!')
        except Exception as e:
            messages.error(request, f'Error creating service: {str(e)}')
        
        return redirect('admin_settings')
    return render(request, 'add_service.html')

@admin_required
def edit_service(request, service_id):
    service = get_object_or_404(SchoolClass, id=service_id)
    if request.method == 'POST':
        new_name = request.POST.get('name')
        new_code = request.POST.get('code')
        
        # Check if new code conflicts with another class
        if new_code != service.code and SchoolClass.objects.filter(code=new_code).exists():
            messages.error(request, f'A service with code "{new_code}" already exists. Please use a unique code.')
            return render(request, 'edit_service.html', {'service': service})
        
        try:
            service.name = new_name
            service.code = new_code
            service.save()
            messages.success(request, f'Service "{new_name}" updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating service: {str(e)}')
        
        return redirect('admin_settings')
    return render(request, 'edit_service.html', {'service': service})

@admin_required
def delete_service(request, service_id):
    service = get_object_or_404(SchoolClass, id=service_id)
    service.delete()
    return redirect('admin_settings')

@admin_required
def add_admin(request):
    # Only superusers can add admins
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can add admins.')
        return redirect('admin_settings')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Ensure profile exists before setting role
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user, role='admin')
        else:
            user.profile.role = 'admin'
            user.profile.save()
        
        messages.success(request, f'Admin user {username} created successfully.')
        return redirect('admin_settings')
    return render(request, 'add_admin.html')

@admin_required
def remove_admin(request, admin_id):
    # Only superusers can remove admins
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can remove admins.')
        return redirect('admin_settings')
    
    admin = get_object_or_404(User, id=admin_id)
    
    # Prevent removing yourself
    if admin.id == request.user.id:
        messages.error(request, 'You cannot remove yourself.')
        return redirect('admin_settings')
    
    # Only allow removal if target is not a superuser or current user is superuser
    if not admin.is_superuser or request.user.is_superuser:
        username = admin.username
        admin.delete()
        messages.success(request, f'Admin user {username} removed successfully.')
    else:
        messages.error(request, 'Cannot remove a superuser.')
    
    return redirect('admin_settings')

@admin_required
def admin_offline_attendance(request):
    """Offline attendance page - caches member and service data"""
    # Get all members
    members = Profile.objects.filter(role='member').only('id', 'name', 'phone')
    members_list = [
        {'id': m.id, 'name': m.name, 'phone': m.phone}
        for m in members
    ]
    
    # Get all active classes
    services = SchoolClass.objects.all().only('id', 'name', 'code')
    services_list = [
        {'id': s.id, 'name': s.name, 'code': s.code}
        for s in services
    ]
    
    context = {
        'members_json': json.dumps(members_list),
        'services_json': json.dumps(services_list),
        'services': services,
    }
    
    return render(request, 'admin_offline_attendance.html', context)

@admin_required
@require_POST
def sync_offline_attendance(request):
    """API endpoint to sync offline attendance records"""
    try:
        data = json.loads(request.body)
        attendance_list = data.get('attendance', [])
        
        if not attendance_list:
            return JsonResponse({'success': False, 'error': 'No attendance data provided'})
        
        synced_count = 0
        errors = []
        
        for item in attendance_list:
            try:
                # Validate required fields
                member_id = item.get('member_id')
                service_id = item.get('service_id')
                timestamp_str = item.get('timestamp')
                
                if not all([member_id, service_id, timestamp_str]):
                    errors.append(f"Missing required fields for {item.get('member_name', 'Unknown')}")
                    continue
                
                # Get member and class
                member = Profile.objects.get(id=member_id)
                service = SchoolClass.objects.get(id=service_id)
                
                # Parse timestamp
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                
                # Check if attendance already exists (prevent duplicates)
                existing = MemberAttendance.objects.filter(
                    phone=member.phone,
                    service=service,
                    timestamp__date=timestamp.date()
                ).exists()
                
                if existing:
                    continue  # Skip duplicates
                
                # Create attendance record
                MemberAttendance.objects.create(
                    name=member.name,
                    phone=member.phone,
                    service=service,
                    service_code=service.code,
                    timestamp=timestamp
                )
                
                synced_count += 1
                
            except Profile.DoesNotExist:
                errors.append(f"Member not found: {item.get('member_name', 'Unknown')}")
            except SchoolClass.DoesNotExist:
                errors.append(f"Class not found: {item.get('service_name', 'Unknown')}")
            except Exception as e:
                errors.append(f"Error syncing {item.get('member_name', 'Unknown')}: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'synced_count': synced_count,
            'errors': errors if errors else None
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ==================== IP GEOLOCATION VIEWS ====================

@admin_required
def admin_geolocation_dashboard(request):
    """
    Dashboard showing IP geolocation analytics for logins and attendance.
    GPS is the primary location source, IP geolocation is fallback.
    """
    from .models_geolocation import LoginLocation, AttendanceLocation, IPGeolocation
    from .geolocation_service import get_location_stats
    from django.conf import settings
    
    # Get location statistics
    stats = get_location_stats()
    
    # Add GPS-specific stats
    stats['gps_attendance_count'] = AttendanceLocation.objects.filter(
        device_latitude__isnull=False,
        device_longitude__isnull=False
    ).count()
    stats['no_gps_attendance_count'] = AttendanceLocation.objects.filter(
        device_latitude__isnull=True
    ).count()
    stats['within_geofence_count'] = AttendanceLocation.objects.filter(
        is_within_geofence=True
    ).count()
    
    # Recent logins with location (last 50)
    recent_logins = LoginLocation.objects.select_related(
        'user', 'geolocation'
    ).order_by('-login_time')[:50]
    
    # Recent attendance locations (last 50)
    recent_attendance = AttendanceLocation.objects.select_related(
        'geolocation', 'geofence'
    ).order_by('-timestamp')[:50]
    
    # Get unique countries and cities for map display
    login_locations_map = LoginLocation.objects.filter(
        geolocation__isnull=False,
        geolocation__latitude__isnull=False
    ).select_related('geolocation').values(
        'geolocation__city', 
        'geolocation__country',
        'geolocation__latitude',
        'geolocation__longitude'
    ).annotate(count=Count('id')).order_by('-count')[:100]
    
    # For attendance, prefer GPS coordinates over IP geolocation
    attendance_locations_map = AttendanceLocation.objects.filter(
        geolocation__isnull=False,
        geolocation__latitude__isnull=False
    ).select_related('geolocation').values(
        'geolocation__city',
        'geolocation__country', 
        'geolocation__latitude',
        'geolocation__longitude'
    ).annotate(count=Count('id')).order_by('-count')[:100]
    
    # Prepare map data for JavaScript - include GPS locations
    map_data = []
    seen_locations = set()
    
    # Add GPS-based attendance locations first (more accurate)
    gps_attendance = AttendanceLocation.objects.filter(
        device_latitude__isnull=False,
        device_longitude__isnull=False
    ).values(
        'device_latitude',
        'device_longitude',
        'member_name'
    ).order_by('-timestamp')[:100]
    
    for loc in gps_attendance:
        lat = float(loc['device_latitude'])
        lng = float(loc['device_longitude'])
        # Round to 4 decimal places to group nearby points
        key = (round(lat, 4), round(lng, 4))
        if key not in seen_locations:
            seen_locations.add(key)
            map_data.append({
                'lat': lat,
                'lng': lng,
                'city': 'GPS Location',
                'country': loc['member_name'],
                'count': 1,
                'is_gps': True
            })
    
    # Then add IP-based locations
    for loc in list(login_locations_map) + list(attendance_locations_map):
        key = (round(float(loc['geolocation__latitude']), 4), round(float(loc['geolocation__longitude']), 4))
        if key not in seen_locations:
            seen_locations.add(key)
            map_data.append({
                'lat': float(loc['geolocation__latitude']),
                'lng': float(loc['geolocation__longitude']),
                'city': loc['geolocation__city'],
                'country': loc['geolocation__country'],
                'count': loc['count'],
                'is_gps': False
            })
    
    # Suspicious activity alerts
    suspicious_logins = LoginLocation.objects.filter(
        geolocation__is_proxy=True
    ).select_related('user', 'geolocation').order_by('-login_time')[:10]
    
    # Export CSV if requested
    if request.GET.get('export') == 'login_csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="login_locations.csv"'
        writer = csv.writer(response)
        writer.writerow(['Username', 'IP Address', 'City', 'Country', 'ISP', 'Login Time', 'Is Proxy', 'Is Mobile'])
        for login in LoginLocation.objects.select_related('user', 'geolocation').order_by('-login_time')[:500]:
            geo = login.geolocation
            writer.writerow([
                login.user.username,
                login.ip_address,
                geo.city if geo else 'N/A',
                geo.country if geo else 'N/A',
                geo.isp if geo else 'N/A',
                login.login_time.strftime('%Y-%m-%d %H:%M:%S'),
                geo.is_proxy if geo else 'N/A',
                geo.is_mobile if geo else 'N/A'
            ])
        return response
    
    if request.GET.get('export') == 'attendance_csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance_locations.csv"'
        writer = csv.writer(response)
        writer.writerow(['Member Name', 'Phone', 'Service', 'IP Address', 'GPS Lat', 'GPS Lng', 'GPS Accuracy', 'IP City', 'IP Country', 'Time', 'Within Geofence', 'Distance'])
        for att in AttendanceLocation.objects.select_related('geolocation').order_by('-timestamp')[:500]:
            geo = att.geolocation
            writer.writerow([
                att.member_name,
                att.member_phone,
                att.service_name or 'N/A',
                att.ip_address,
                att.device_latitude or 'N/A',
                att.device_longitude or 'N/A',
                f'{att.gps_accuracy}m' if att.gps_accuracy else 'N/A',
                geo.city if geo else 'N/A',
                geo.country if geo else 'N/A',
                att.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if att.is_within_geofence else 'No',
                f'{att.distance_from_site:.0f}m' if att.distance_from_site else 'N/A'
            ])
        return response
    
    # Get user's current IP for testing
    from .geolocation_service import get_client_ip, is_private_ip
    user_ip = get_client_ip(request)
    
    context = {
        'stats': stats,
        'recent_logins': recent_logins,
        'recent_attendance': recent_attendance,
        'map_data_json': json.dumps(map_data),
        'suspicious_logins': suspicious_logins,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
        'your_ip': user_ip,
        'is_private_ip': is_private_ip(user_ip),
    }
    
    return render(request, 'admin_geolocation.html', context)


@admin_required
def member_location_history(request, member_phone):
    """
    View location history for a specific member by phone number.
    """
    from .models_geolocation import AttendanceLocation
    
    # URL decode the phone number
    import urllib.parse
    member_phone = urllib.parse.unquote(member_phone)
    
    # Get member profile
    member = get_object_or_404(Profile, phone=member_phone, role='member')
    
    # Get all attendance locations for this member
    locations = AttendanceLocation.objects.filter(
        member_phone=member_phone
    ).select_related('geolocation').order_by('-timestamp')
    
    # Get unique locations
    unique_locations = AttendanceLocation.objects.filter(
        member_phone=member_phone,
        geolocation__isnull=False
    ).values(
        'geolocation__city',
        'geolocation__country',
        'geolocation__latitude',
        'geolocation__longitude'
    ).annotate(count=Count('id')).order_by('-count')
    
    context = {
        'member': member,
        'locations': locations,
        'unique_locations': unique_locations,
        'total_checkins': locations.count(),
    }
    
    return render(request, 'member_location_history.html', context)


@admin_required
def user_login_history(request, user_id):
    """
    View login location history for a specific admin user.
    """
    from .models_geolocation import LoginLocation
    
    user = get_object_or_404(User, id=user_id)
    
    # Get all login locations for this user
    logins = LoginLocation.objects.filter(
        user=user
    ).select_related('geolocation').order_by('-login_time')
    
    # Get unique locations
    unique_locations = LoginLocation.objects.filter(
        user=user,
        geolocation__isnull=False
    ).values(
        'geolocation__city',
        'geolocation__country',
        'geolocation__latitude',
        'geolocation__longitude'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Detect suspicious activity (different cities in short time)
    suspicious_activity = []
    logins_list = list(logins[:50])
    for i in range(len(logins_list) - 1):
        current = logins_list[i]
        previous = logins_list[i + 1]
        
        if current.geolocation and previous.geolocation:
            # Check if different city within 1 hour
            time_diff = current.login_time - previous.login_time
            if time_diff.total_seconds() < 3600:  # 1 hour
                if current.geolocation.city != previous.geolocation.city:
                    suspicious_activity.append({
                        'current': current,
                        'previous': previous,
                        'time_diff_minutes': int(time_diff.total_seconds() / 60)
                    })
    
    context = {
        'target_user': user,
        'logins': logins,
        'unique_locations': unique_locations,
        'total_logins': logins.count(),
        'suspicious_activity': suspicious_activity,
    }
    
    return render(request, 'user_login_history.html', context)


# ==================== GEOFENCE MANAGEMENT VIEWS ====================

@admin_required
def geofence_list(request):
    """
    List all geofence locations with management options.
    """
    from .models_geolocation import Geofence, AttendanceLocation
    from django.conf import settings
    
    geofences = Geofence.objects.all().order_by('-is_active', 'name')
    
    # Get check-in stats for each geofence
    geofence_stats = {}
    for gf in geofences:
        stats = AttendanceLocation.objects.filter(geofence=gf).aggregate(
            total=Count('id'),
            within=Count('id', filter=models.Q(is_within_geofence=True)),
            outside=Count('id', filter=models.Q(is_within_geofence=False))
        )
        geofence_stats[gf.id] = stats
    
    # Prepare geofences data for map
    geofences_map_data = [
        {
            'id': gf.id,
            'name': gf.name,
            'lat': float(gf.latitude),
            'lng': float(gf.longitude),
            'radius': gf.radius,
            'site_type': gf.site_type,
            'is_active': gf.is_active,
            'address': gf.full_address
        }
        for gf in geofences
    ]
    
    context = {
        'geofences': geofences,
        'geofence_stats': geofence_stats,
        'geofences_json': json.dumps(geofences_map_data),
        'total_active': geofences.filter(is_active=True).count(),
        'total_inactive': geofences.filter(is_active=False).count(),
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    
    return render(request, 'geofence_list.html', context)


@admin_required
def geofence_add(request):
    """
    Add a new geofence location.
    Supports setting location via map click or manual coordinates.
    """
    from .models_geolocation import Geofence
    from django.conf import settings
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            site_type = request.POST.get('site_type', 'office')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            radius = request.POST.get('radius', 100)
            address = request.POST.get('address', '')
            city = request.POST.get('city', '')
            state = request.POST.get('state', '')
            country = request.POST.get('country', '')
            postal_code = request.POST.get('postal_code', '')
            is_active = request.POST.get('is_active') == 'on'
            require_gps = request.POST.get('require_gps') == 'on'
            allow_remote = request.POST.get('allow_remote') == 'on'
            
            # Validate required fields
            if not name or not latitude or not longitude:
                messages.error(request, 'Name, latitude, and longitude are required.')
                return render(request, 'geofence_add.html', {
                    'site_types': Geofence.SITE_TYPES,
                    'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
                })
            
            # Create geofence
            geofence = Geofence.objects.create(
                name=name,
                description=description,
                site_type=site_type,
                latitude=latitude,
                longitude=longitude,
                radius=int(radius),
                address=address,
                city=city,
                state=state,
                country=country,
                postal_code=postal_code,
                is_active=is_active,
                require_gps=require_gps,
                allow_remote=allow_remote,
                created_by=request.user
            )
            
            messages.success(request, f'Location "{name}" created successfully!')
            return redirect('geofence_list')
            
        except Exception as e:
            messages.error(request, f'Error creating location: {str(e)}')
    
    context = {
        'site_types': Geofence.SITE_TYPES,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    
    return render(request, 'geofence_add.html', context)


@admin_required
def geofence_edit(request, geofence_id):
    """
    Edit an existing geofence location.
    """
    from .models_geolocation import Geofence
    from django.conf import settings
    
    geofence = get_object_or_404(Geofence, id=geofence_id)
    
    if request.method == 'POST':
        try:
            geofence.name = request.POST.get('name')
            geofence.description = request.POST.get('description', '')
            geofence.site_type = request.POST.get('site_type', 'office')
            geofence.latitude = request.POST.get('latitude')
            geofence.longitude = request.POST.get('longitude')
            geofence.radius = int(request.POST.get('radius', 100))
            geofence.address = request.POST.get('address', '')
            geofence.city = request.POST.get('city', '')
            geofence.state = request.POST.get('state', '')
            geofence.country = request.POST.get('country', '')
            geofence.postal_code = request.POST.get('postal_code', '')
            geofence.is_active = request.POST.get('is_active') == 'on'
            geofence.require_gps = request.POST.get('require_gps') == 'on'
            geofence.allow_remote = request.POST.get('allow_remote') == 'on'
            
            geofence.save()
            
            messages.success(request, f'Location "{geofence.name}" updated successfully!')
            return redirect('geofence_list')
            
        except Exception as e:
            messages.error(request, f'Error updating location: {str(e)}')
    
    context = {
        'geofence': geofence,
        'site_types': Geofence.SITE_TYPES,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    
    return render(request, 'geofence_edit.html', context)


@admin_required
def geofence_delete(request, geofence_id):
    """
    Delete a geofence location.
    """
    from .models_geolocation import Geofence
    
    geofence = get_object_or_404(Geofence, id=geofence_id)
    name = geofence.name
    geofence.delete()
    
    messages.success(request, f'Location "{name}" deleted successfully!')
    return redirect('geofence_list')


@admin_required
def geofence_toggle(request, geofence_id):
    """
    Toggle geofence active status.
    """
    from .models_geolocation import Geofence
    
    geofence = get_object_or_404(Geofence, id=geofence_id)
    geofence.is_active = not geofence.is_active
    geofence.save()
    
    status = "activated" if geofence.is_active else "deactivated"
    messages.success(request, f'Location "{geofence.name}" {status}!')
    
    return redirect('geofence_list')


@csrf_exempt
@require_POST
def api_validate_location(request):
    """
    API endpoint to validate if coordinates are within any active geofence.
    Used for real-time GPS check-in validation.
    """
    from .models_geolocation import Geofence
    
    try:
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        geofence_id = data.get('geofence_id')  # Optional specific geofence
        
        if latitude is None or longitude is None:
            return JsonResponse({
                'valid': False,
                'error': 'Latitude and longitude are required'
            })
        
        # Check specific geofence or all active geofences
        if geofence_id:
            geofences = Geofence.objects.filter(id=geofence_id, is_active=True)
        else:
            geofences = Geofence.objects.filter(is_active=True)
        
        matching_geofences = []
        nearest_geofence = None
        min_distance = float('inf')
        
        for gf in geofences:
            distance = gf.calculate_distance(latitude, longitude)
            
            if distance < min_distance:
                min_distance = distance
                nearest_geofence = gf
            
            if gf.is_within_geofence(latitude, longitude):
                matching_geofences.append({
                    'id': gf.id,
                    'name': gf.name,
                    'site_type': gf.site_type,
                    'distance': round(distance, 2),
                    'radius': gf.radius
                })
        
        response = {
            'valid': len(matching_geofences) > 0,
            'matching_locations': matching_geofences,
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            }
        }
        
        if nearest_geofence and not matching_geofences:
            response['nearest'] = {
                'id': nearest_geofence.id,
                'name': nearest_geofence.name,
                'distance': round(min_distance, 2),
                'radius': nearest_geofence.radius
            }
        
        return JsonResponse(response)
        
    except json.JSONDecodeError:
        return JsonResponse({'valid': False, 'error': 'Invalid JSON'})
    except Exception as e:
        return JsonResponse({'valid': False, 'error': str(e)})


@csrf_exempt
@require_POST  
def api_reverse_geocode(request):
    """
    API endpoint to get address from coordinates using Nominatim (OpenStreetMap).
    """
    import requests as http_requests
    
    try:
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is None or longitude is None:
            return JsonResponse({'error': 'Coordinates required'}, status=400)
        
        # Use Nominatim for reverse geocoding (free, no API key)
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
        headers = {'User-Agent': 'RollCall-AttendanceSystem/1.0'}
        
        response = http_requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            return JsonResponse({
                'success': True,
                'display_name': data.get('display_name', ''),
                'address': {
                    'road': address.get('road', ''),
                    'city': address.get('city') or address.get('town') or address.get('village', ''),
                    'state': address.get('state', ''),
                    'country': address.get('country', ''),
                    'postal_code': address.get('postcode', '')
                }
            })
        else:
            return JsonResponse({'error': 'Geocoding failed'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
