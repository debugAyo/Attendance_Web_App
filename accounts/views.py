from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm
from .models import UserActivity, Profile
from attendance.models import Attendance, MemberAttendance
from datetime import date
import json

# Custom login view
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        user = form.get_user()
        # Allow superusers or users with admin role to log in
        if user.is_superuser or (hasattr(user, 'profile') and getattr(user.profile, 'role', None) == 'admin'):
            response = super().form_valid(form)
            UserActivity.objects.create(user=self.request.user)
            return response
        else:
            from django.contrib import messages
            messages.error(self.request, 'Only admins are allowed to log in.')
            return redirect('login')

# Public landing page
def landing(request):
    """Landing page showing login/signup links for non-logged-in users"""
    if request.user.is_authenticated:
        return redirect('home')  # redirect logged-in users to dashboard
    return render(request, 'accounts/landing.html')

# Dashboard/home page (after login)
@login_required
def home(request):
    """Dashboard showing comprehensive attendance analytics for admins."""
    context = {}
    # Allow superusers or users with admin role to access dashboard
    if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        from django.db.models import Count, Q
        from datetime import timedelta
        
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # === TODAY'S ATTENDANCE ===
        todays_attendance = MemberAttendance.objects.filter(timestamp__date=today).select_related('service')
        
        # Service breakdown for today
        service_breakdown = MemberAttendance.objects.filter(
            timestamp__date=today
        ).values(
            'service__name', 'service_code', 'timestamp__date'
        ).annotate(
            total=Count('id')
        ).order_by('service__name')
        
        # === GENDER/AGE BREAKDOWN ===
        male = female = children = 0
        phone_numbers = todays_attendance.values_list('phone', flat=True).distinct()
        profiles = Profile.objects.filter(phone__in=phone_numbers, role='member')
        
        for profile in profiles:
            age = get_age(profile.date_of_birth)
            gender = profile.gender.lower() if profile.gender else ''
            
            if gender == 'male':
                if age is not None and age < 13:
                    children += 1
                else:
                    male += 1
            elif gender == 'female':
                if age is not None and age < 13:
                    children += 1
                else:
                    female += 1
            else:
                if age is not None and age < 13:
                    children += 1
        
        # === MONTHLY TRENDS (Last 30 days) ===
        monthly_labels = []
        monthly_data = []
        for i in range(29, -1, -1):
            day = today - timedelta(days=i)
            monthly_labels.append(day.strftime('%b %d'))
            count = MemberAttendance.objects.filter(timestamp__date=day).count()
            monthly_data.append(count)
        
        # === ENGAGEMENT METRICS ===
        # Most active members (top 5)
        top_members = MemberAttendance.objects.values('name', 'phone').annotate(
            total=Count('id')
        ).order_by('-total')[:5]
        
        # Inactive members (haven't attended in 30 days)
        recent_phones = MemberAttendance.objects.filter(
            timestamp__gte=month_ago
        ).values_list('phone', flat=True).distinct()
        inactive_members = Profile.objects.filter(
            role='member'
        ).exclude(phone__in=recent_phones)[:10]
        
        # === MEMBER GROWTH ===
        # New members per week (last 4 weeks)
        growth_labels = []
        growth_data = []
        for week in range(3, -1, -1):
            week_start = today - timedelta(days=week*7+6)
            week_end = today - timedelta(days=week*7)
            growth_labels.append(f"{week_start.strftime('%b %d')}")
            count = Profile.objects.filter(
                role='member',
                first_visit_date__gte=week_start,
                first_visit_date__lte=week_end
            ).count()
            growth_data.append(count)
        
        # === SERVICE COMPARISON ===
        # Compare attendance across all services (this month)
        service_comparison = MemberAttendance.objects.filter(
            timestamp__gte=month_ago
        ).values('service__name').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # === ALERTS ===
        alerts = []
        
        # === ABSENTEE DETECTION (Missed 2+ Consecutive Services) ===
        # Get the last 3 services (to check for 2 consecutive misses)
        from attendance.models import ChurchService
        recent_services = ChurchService.objects.all().order_by('-id')[:3]
        
        absentee_members = []
        if recent_services.count() >= 2:
            # Get all members
            all_members = Profile.objects.filter(role='member')
            
            # For each member, check if they missed last 2 services
            for member in all_members:
                # Get member's attendance for recent services
                member_recent_attendance = MemberAttendance.objects.filter(
                    phone=member.phone,
                    service__in=recent_services
                ).values_list('service_id', flat=True)
                
                # Check if member missed the last 2 services
                if recent_services.count() >= 2:
                    last_two_services = list(recent_services[:2])
                    attended_last_two = any(
                        service.id in member_recent_attendance 
                        for service in last_two_services
                    )
                    
                    if not attended_last_two:
                        # Calculate age for child detection
                        age = get_age(member.date_of_birth)
                        absentee_members.append({
                            'name': member.name,
                            'phone': member.phone,
                            'email': member.email,
                            'last_attendance': MemberAttendance.objects.filter(
                                phone=member.phone
                            ).order_by('-timestamp').first(),
                            'age': age,
                            'is_child': age and age < 13
                        })
        
        # Low attendance alert (if today < 50% of average)
        avg_attendance = MemberAttendance.objects.filter(
            timestamp__gte=week_ago
        ).values('timestamp__date').annotate(
            daily_count=Count('id')
        ).aggregate(avg=Count('id'))
        
        total_members = Profile.objects.filter(role='member').count()
        first_timers_week = Profile.objects.filter(
            role='member',
            is_first_timer=True,
            first_visit_date__gte=week_ago
        ).count()
        
        # Calculate percentages
        total_attendance_today = male + female + children
        male_percentage = round((male / total_attendance_today * 100), 1) if total_attendance_today > 0 else 0
        female_percentage = round((female / total_attendance_today * 100), 1) if total_attendance_today > 0 else 0
        children_percentage = round((children / total_attendance_today * 100), 1) if total_attendance_today > 0 else 0
        
        # New members this month
        new_members_this_month = Profile.objects.filter(
            role='member',
            first_visit_date__gte=month_ago,
            first_visit_date__lte=today
        ).count()
        
        # Service attendance (all services with breakdown)
        service_attendance = MemberAttendance.objects.values(
            'service__name', 'timestamp__date', 'service__code'
        ).annotate(
            total=Count('id')
        ).order_by('-timestamp__date')[:10]
        
        # Build context
        context.update({
            'user_activities': UserActivity.objects.order_by('-login_time')[:10],
            'todays_attendance': todays_attendance,
            'todays_attendance_count': todays_attendance.count(),
            'service_breakdown': service_breakdown,
            'male_count': male,
            'female_count': female,
            'children_count': children,
            'male_percentage': male_percentage,
            'female_percentage': female_percentage,
            'children_percentage': children_percentage,
            'total_attendance': MemberAttendance.objects.count(),
            'today': today,
            'monthly_labels': json.dumps(monthly_labels),
            'monthly_data': json.dumps(monthly_data),
            'top_members': top_members,
            'inactive_members': inactive_members,
            'growth_labels': json.dumps(growth_labels),
            'growth_data': json.dumps(growth_data),
            'service_comparison': service_comparison,
            'service_attendance': service_attendance,
            'total_members': total_members,
            'first_timers_week': first_timers_week,
            'new_members_this_month': new_members_this_month,
            'absentee_members': absentee_members,
            'alerts': alerts
        })
    return render(request, 'dashboard.html', context)

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            if role == 'admin':
                # SECURITY: Only allow admin creation via invite or superuser approval
                messages.error(request, 'Admin accounts can only be created by the system administrator. Please contact your church administrator.')
                return redirect('signup')
            elif role == 'member':
                # Create a MemberProfile (no login, no user account)
                from .models import Profile
                name = form.cleaned_data.get('name')
                phone = form.cleaned_data.get('phone')
                gender = form.cleaned_data.get('gender')
                dob = form.cleaned_data.get('date_of_birth')
                wedding_anniversary = form.cleaned_data.get('wedding_anniversary')
                member_email = form.cleaned_data.get('member_email')
                how_heard = form.cleaned_data.get('how_heard')
                how_heard_other = form.cleaned_data.get('how_heard_other')
                
                # Check if member already exists
                existing = Profile.objects.filter(phone=phone, role='member').first()
                if existing:
                    messages.warning(request, f'A member with phone number {phone} already exists.')
                    return redirect('signup')
                
                Profile.objects.create(
                    user=None,  # No user account
                    role='member',
                    name=name,
                    phone=phone,
                    gender=gender,
                    date_of_birth=dob,
                    wedding_anniversary=wedding_anniversary,
                    email=member_email,
                    how_heard=how_heard if how_heard else None,
                    how_heard_other=how_heard_other if how_heard_other else None
                )
                return render(request, 'accounts/signup_success.html', {'name': name})
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def get_age(dob):
    if not dob:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

# Custom logout view
def custom_logout(request):
    """Logout view that properly handles user logout and redirects to landing page"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('landing')
