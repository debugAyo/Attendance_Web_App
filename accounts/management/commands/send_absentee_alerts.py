from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import Profile
from attendance.models import MemberAttendance, ChurchService
from datetime import date


class Command(BaseCommand):
    help = 'Check for students who missed the last 2 consecutive classes and send email alerts to admins'

    def handle(self, *args, **options):
        # Get all admin emails
        admin_profiles = Profile.objects.filter(role='admin').exclude(email__isnull=True).exclude(email='')
        admin_emails = [profile.email for profile in admin_profiles if profile.email]
        
        if not admin_emails:
            self.stdout.write(self.style.WARNING('No admin emails found. Please add admin emails.'))
            return
        
        # Get recent classes (last 3)
        recent_services = ChurchService.objects.all().order_by('-id')[:3]
        
        if recent_services.count() < 2:
            self.stdout.write(self.style.WARNING('Not enough classes to check for absentees.'))
            return
        
        # Get all members
        all_members = Profile.objects.filter(role='member')
        absentee_members = []
        
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
                    # Get last attendance
                    last_attendance = MemberAttendance.objects.filter(
                        phone=member.phone
                    ).order_by('-timestamp').first()
                    
                    absentee_members.append({
                        'name': member.name,
                        'phone': member.phone,
                        'email': member.email,
                        'last_attendance': last_attendance.timestamp if last_attendance else None
                    })
        
        if not absentee_members:
            self.stdout.write(self.style.SUCCESS('✓ All members are active! No absentees to report.'))
            return
        
        # Compose email
        subject = f'⚠️ Absentee Alert: {len(absentee_members)} Student(s) Missing for 2+ Classes'
        
        message = f"""
School Attendance Alert
=======================

The following {len(absentee_members)} student(s) have not attended the last 2 consecutive classes:

"""
        for i, member in enumerate(absentee_members, 1):
            message += f"\n{i}. {member['name']}"
            message += f"\n   Phone: {member['phone']}"
            if member['email']:
                message += f"\n   Email: {member['email']}"
            if member['last_attendance']:
                message += f"\n   Last Attended: {member['last_attendance'].strftime('%B %d, %Y at %I:%M %p')}"
            else:
                message += f"\n   Last Attended: Never"
            message += "\n"
        
        message += f"""
---
Please follow up with these members to ensure their well-being.

This is an automated alert from the RollCall Attendance System.
Generated on: {date.today().strftime('%B %d, %Y')}
        """
        
        # Send email
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Absentee alert sent to {len(admin_emails)} admin(s): {", ".join(admin_emails)}'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f'  {len(absentee_members)} absentee member(s) reported.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send email: {str(e)}')
            )
            self.stdout.write(
                self.style.ERROR('  Please check your email settings in settings.py')
            )
