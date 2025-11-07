from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import AttendanceForm
from .models import Attendance
from django.contrib import messages

def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'

@login_required
@user_passes_test(is_admin)
def mark_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            service = form.cleaned_data['service']
            date = form.cleaned_data['date']
            attendees = form.cleaned_data['attendees']
            attendance_obj, created = Attendance.objects.get_or_create(service=service, date=date)
            attendance_obj.attendees.set(attendees)
            attendance_obj.save()
            messages.success(request, 'Attendance has been recorded!')
            return redirect('mark_attendance')
    else:
        form = AttendanceForm()
    return render(request, 'attendance/mark_attendance.html', {'form': form})