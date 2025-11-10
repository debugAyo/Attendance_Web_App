from django.shortcuts import render, redirect, get_object_or_404
from attendance.models import MemberAttendance, ChurchService
from accounts.models import Profile
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count
from datetime import datetime, timedelta, date
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import csv
import json

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

def remove_member(request, member_id):
    member = get_object_or_404(Profile, id=member_id, role='member')
    member.delete()
    return redirect('admin_manage_members')

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
        
        # Handle wedding anniversary
        anniversary = request.POST.get('wedding_anniversary')
        if anniversary:
            member.wedding_anniversary = anniversary
        else:
            member.wedding_anniversary = None
        
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

def remove_attendance(request, attendance_id):
    attendance = get_object_or_404(MemberAttendance, id=attendance_id)
    attendance.delete()
    return redirect('admin_todays_attendance')

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
    
    # Upcoming wedding anniversaries (next 30 days)
    upcoming_anniversaries = []
    members_with_anniversary = Profile.objects.filter(
        role='member',
        wedding_anniversary__isnull=False
    ).only('name', 'phone', 'wedding_anniversary')
    
    for member in members_with_anniversary:
        # Calculate next anniversary
        next_anniversary = member.wedding_anniversary.replace(year=today.year)
        if next_anniversary < today:
            next_anniversary = member.wedding_anniversary.replace(year=today.year + 1)
        
        days_until = (next_anniversary - today).days
        if 0 <= days_until <= 30:
            # Calculate years of marriage
            years_married = today.year - member.wedding_anniversary.year
            if next_anniversary > today:
                years_married = today.year - member.wedding_anniversary.year
            else:
                years_married = today.year - member.wedding_anniversary.year + 1
            
            upcoming_anniversaries.append({
                'name': member.name,
                'phone': member.phone,
                'date': next_anniversary,
                'days_until': days_until,
                'years': years_married
            })
    
    upcoming_anniversaries.sort(key=lambda x: x['days_until'])
    
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
        'upcoming_anniversaries': upcoming_anniversaries[:5],  # Show only top 5
        'top_attendees': top_attendees,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'admin_summary.html', context)

def admin_settings(request):
    # Optimized queries - only fetch needed fields
    services = ChurchService.objects.all().only('id', 'name', 'code')
    
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

def add_service(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        ChurchService.objects.create(name=name, code=code)
        return redirect('admin_settings')
    return render(request, 'add_service.html')

def edit_service(request, service_id):
    service = get_object_or_404(ChurchService, id=service_id)
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.code = request.POST.get('code')
        service.save()
        return redirect('admin_settings')
    return render(request, 'edit_service.html', {'service': service})

def delete_service(request, service_id):
    service = get_object_or_404(ChurchService, id=service_id)
    service.delete()
    return redirect('admin_settings')

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

def admin_offline_attendance(request):
    """Offline attendance page - caches member and service data"""
    # Get all members
    members = Profile.objects.filter(role='member').only('id', 'name', 'phone')
    members_list = [
        {'id': m.id, 'name': m.name, 'phone': m.phone}
        for m in members
    ]
    
    # Get all active services
    services = ChurchService.objects.all().only('id', 'name', 'code')
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
                
                # Get member and service
                member = Profile.objects.get(id=member_id)
                service = ChurchService.objects.get(id=service_id)
                
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
            except ChurchService.DoesNotExist:
                errors.append(f"Service not found: {item.get('service_name', 'Unknown')}")
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
