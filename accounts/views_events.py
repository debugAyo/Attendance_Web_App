from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChurchEvent, EventRegistration
from datetime import date, timedelta
import calendar


@login_required
def events_calendar(request):
    """Display calendar of church events."""
    today = date.today()
    
    # Get month and year from request, default to current
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    # Get all events for the selected month
    events_this_month = ChurchEvent.objects.filter(
        start_date__year=year,
        start_date__month=month,
        is_active=True
    )
    
    # Get upcoming events (next 30 days)
    upcoming_events = ChurchEvent.objects.filter(
        start_date__gte=today,
        start_date__lte=today + timedelta(days=30),
        is_active=True
    )[:10]
    
    # Get events happening today
    todays_events = ChurchEvent.objects.filter(
        start_date=today,
        is_active=True
    )
    
    # Calendar navigation
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Previous and next month calculations
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year
    
    # Group events by date for easy lookup
    events_by_date = {}
    for event in events_this_month:
        date_key = event.start_date.day
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)
    
    context = {
        'calendar': cal,
        'month': month,
        'year': year,
        'month_name': month_name,
        'today': today,
        'events_by_date': events_by_date,
        'upcoming_events': upcoming_events,
        'todays_events': todays_events,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    
    return render(request, 'events_calendar.html', context)


@login_required
def add_event(request):
    """Add a new church event."""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_type = request.POST.get('event_type')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date') or None
        end_time = request.POST.get('end_time') or None
        location = request.POST.get('location')
        organizer = request.POST.get('organizer')
        is_recurring = request.POST.get('is_recurring') == 'on'
        recurring_pattern = request.POST.get('recurring_pattern')
        max_attendees = request.POST.get('max_attendees') or None
        registration_required = request.POST.get('registration_required') == 'on'
        
        ChurchEvent.objects.create(
            title=title,
            description=description,
            event_type=event_type,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            location=location,
            organizer=organizer,
            is_recurring=is_recurring,
            recurring_pattern=recurring_pattern,
            max_attendees=max_attendees,
            registration_required=registration_required,
        )
        
        messages.success(request, f'Event "{title}" created successfully!')
        return redirect('events_calendar')
    
    return render(request, 'add_event.html', {
        'event_types': ChurchEvent.EVENT_TYPES
    })


@login_required
def event_detail(request, event_id):
    """View event details and registrations."""
    event = get_object_or_404(ChurchEvent, id=event_id)
    registrations = event.registrations.all()
    registration_count = registrations.count()
    
    context = {
        'event': event,
        'registrations': registrations,
        'registration_count': registration_count,
        'spots_remaining': event.max_attendees - registration_count if event.max_attendees else None,
    }
    
    return render(request, 'event_detail.html', context)


@login_required
def register_for_event(request, event_id):
    """Register a member for an event."""
    event = get_object_or_404(ChurchEvent, id=event_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        notes = request.POST.get('notes')
        
        # Check if already registered
        if EventRegistration.objects.filter(event=event, phone=phone).exists():
            messages.warning(request, 'You are already registered for this event.')
            return redirect('event_detail', event_id=event_id)
        
        # Check if event is full
        if event.max_attendees:
            current_registrations = event.registrations.count()
            if current_registrations >= event.max_attendees:
                messages.error(request, 'Sorry, this event is full.')
                return redirect('event_detail', event_id=event_id)
        
        EventRegistration.objects.create(
            event=event,
            name=name,
            phone=phone,
            email=email,
            notes=notes
        )
        
        messages.success(request, f'Successfully registered for "{event.title}"!')
        return redirect('event_detail', event_id=event_id)
    
    return redirect('event_detail', event_id=event_id)


@login_required
def delete_event(request, event_id):
    """Delete a church event."""
    if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        event = get_object_or_404(ChurchEvent, id=event_id)
        event_title = event.title
        event.delete()
        messages.success(request, f'Event "{event_title}" deleted successfully!')
    else:
        messages.error(request, 'Only admins can delete events.')
    
    return redirect('events_calendar')
