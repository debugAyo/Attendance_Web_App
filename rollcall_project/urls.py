
from accounts.admin_views import (admin_manage_members, remove_member, edit_member,
                                  admin_todays_attendance, remove_attendance,
                                  admin_summary, admin_settings, add_service, edit_service,
                                  delete_service, add_admin, remove_admin)
"""
URL configuration for rollcall_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts.views import landing, signup_view, CustomLoginView, home, custom_logout
from accounts.views_events import events_calendar, add_event, event_detail, register_for_event, delete_event
from django.urls import path
from attendance.views import mark_attendance
from attendance.views_member import member_mark_attendance, search_members

urlpatterns = [
    # Custom admin URLs must come BEFORE Django's admin.site.urls
    path('admin/members/', admin_manage_members, name='admin_manage_members'),
    path('admin/members/remove/<int:member_id>/', remove_member, name='remove_member'),
    path('admin/members/edit/<int:member_id>/', edit_member, name='edit_member'),
    path('admin/attendance/today/', admin_todays_attendance, name='admin_todays_attendance'),
    path('admin/attendance/remove/<int:attendance_id>/', remove_attendance, name='remove_attendance'),
    path('admin/summary/', admin_summary, name='admin_summary'),
    path('admin/settings/', admin_settings, name='admin_settings'),
    path('admin/settings/service/add/', add_service, name='add_service'),
    path('admin/settings/service/edit/<int:service_id>/', edit_service, name='edit_service'),
    path('admin/settings/service/delete/<int:service_id>/', delete_service, name='delete_service'),
    path('admin/settings/admin/add/', add_admin, name='add_admin'),
    path('admin/settings/admin/remove/<int:admin_id>/', remove_admin, name='remove_admin'),
    
    # Django admin site - this has a catch-all pattern, so it must come after custom admin URLs
    path('admin/', admin.site.urls),
    
    # Other URLs
    path('', member_mark_attendance, name='landing'),  # Member attendance as homepage
    path('signup/', signup_view, name='signup'), # signup page
    path('login/', CustomLoginView.as_view(), name='login'), # login page
    path('home/', home, name='home'),            # dashboard after login
    path('logout/', custom_logout, name='logout'),
    path('mark/', mark_attendance, name='mark_attendance'),
    path('member/mark/', member_mark_attendance, name='member_mark_attendance'),
    path('api/search-members/', search_members, name='search_members'),
    
    # Events/Calendar URLs
    path('events/', events_calendar, name='events_calendar'),
    path('events/add/', add_event, name='add_event'),
    path('events/<int:event_id>/', event_detail, name='event_detail'),
    path('events/<int:event_id>/register/', register_for_event, name='register_for_event'),
    path('events/<int:event_id>/delete/', delete_event, name='delete_event'),
]






