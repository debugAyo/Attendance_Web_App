from django.shortcuts import render, redirect
from .forms_member import MemberAttendanceForm
from .models import SchoolClass, Attendance
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import Profile
from accounts.geolocation_service import track_attendance_location, get_client_ip, fetch_geolocation
from datetime import date
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

# API endpoint for member search autocomplete
def search_members(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:  # Only search if at least 2 characters
        return JsonResponse({'members': []})
    
    # Search members by name or phone
    members = Profile.objects.filter(role='member').filter(
        name__icontains=query
    ) | Profile.objects.filter(role='member').filter(
        phone__icontains=query
    )
    
    members = members.distinct()[:10]  # Limit to 10 results
    
    member_list = [
        {
            'name': member.name,
            'phone': member.phone,
        }
        for member in members
    ]
    
    return JsonResponse({'members': member_list})


# API endpoint for VPN/Proxy detection
@require_POST
def check_vpn(request):
    """Check if user is connected via VPN/Proxy using IP-API"""
    ip_address = get_client_ip(request)
    
    # Get geolocation data which includes VPN/proxy detection
    geo_data = fetch_geolocation(ip_address)
    
    if geo_data:
        is_vpn = geo_data.get('is_proxy', False)
        is_hosting = geo_data.get('is_hosting', False)
        
        # Build reason string
        reasons = []
        if is_vpn:
            reasons.append('VPN/Proxy detected')
        if is_hosting:
            reasons.append('Datacenter/Hosting IP')
        
        return JsonResponse({
            'is_vpn': is_vpn,
            'is_proxy': is_vpn,
            'is_hosting': is_hosting,
            'reason': ', '.join(reasons) if reasons else None,
            'isp': geo_data.get('isp', ''),
            'org': geo_data.get('org', '')
        })
    
    # Could not determine - allow by default
    return JsonResponse({
        'is_vpn': False,
        'is_proxy': False,
        'is_hosting': False,
        'reason': None
    })

# Member attendance marking (no login required)
def member_mark_attendance(request):
    from .models import MemberAttendance
    
    # Check if coming from signup (pre-fill member info)
    prefill_name = request.session.pop('new_member_name', None)
    prefill_phone = request.session.pop('new_member_phone', None)
    
    if request.method == 'POST':
        form = MemberAttendanceForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            service_code = form.cleaned_data['service_code']
            service = form.cleaned_data['service']
            
            # Get GPS coordinates from hidden form fields
            device_latitude = request.POST.get('device_latitude')
            device_longitude = request.POST.get('device_longitude')
            gps_accuracy = request.POST.get('gps_accuracy')
            
            # Convert to proper types (or None if empty/invalid)
            try:
                device_latitude = float(device_latitude) if device_latitude else None
                device_longitude = float(device_longitude) if device_longitude else None
                gps_accuracy = float(gps_accuracy) if gps_accuracy else None
            except (ValueError, TypeError):
                device_latitude = None
                device_longitude = None
                gps_accuracy = None
            
            # Validate service_code matches the selected service's code
            if service_code != service.code:
                form.add_error('service_code', 'Invalid service code. Please enter the correct code for this service.')
            else:
                # Mark attendance
                MemberAttendance.objects.create(
                    name=name,
                    phone=phone,
                    service=service,
                    service_code=service_code
                )
                
                # Track attendance location with GPS as primary
                track_attendance_location(
                    member_phone=phone,
                    member_name=name,
                    request=request,
                    service_name=service.name,
                    device_latitude=device_latitude,
                    device_longitude=device_longitude,
                    gps_accuracy=gps_accuracy
                )
                
                # Check if this is a returning member and update their status
                member_profile = Profile.objects.filter(phone=phone, role='member').first()
                if member_profile and member_profile.is_first_timer:
                    attendance_count = MemberAttendance.objects.filter(phone=phone).count()
                    if attendance_count >= 2:  # Second attendance marks them as returning
                        member_profile.mark_as_returning_member()
                        messages.success(request, f"Welcome back, {name}! Attendance marked for {service.name}!")
                    else:
                        messages.success(request, f"Welcome first-timer, {name}! Attendance marked for {service.name}!")
                else:
                    messages.success(request, f"Attendance marked for {name} for {service.name}!")
                
                return redirect('member_mark_attendance')
    else:
        form = MemberAttendanceForm()
    
    context = {
        'form': form,
        'prefill_name': prefill_name,
        'prefill_phone': prefill_phone,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    return render(request, 'attendance/member_mark_attendance.html', context)
