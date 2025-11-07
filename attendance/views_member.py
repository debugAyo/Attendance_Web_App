from django.shortcuts import render, redirect
from .forms_member import MemberAttendanceForm
from .models import ChurchService, Attendance
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import Profile
from datetime import date

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

# Member attendance marking (no login required)
def member_mark_attendance(request):
    from .models import MemberAttendance
    if request.method == 'POST':
        form = MemberAttendanceForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            service_code = form.cleaned_data['service_code']
            service = form.cleaned_data['service']
            
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
    return render(request, 'attendance/member_mark_attendance.html', {'form': form})
