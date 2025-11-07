from django.contrib import admin
from .models import MemberAttendance

@admin.register(MemberAttendance)
class MemberAttendanceAdmin(admin.ModelAdmin):
	list_display = ('name', 'phone', 'service', 'service_code', 'timestamp')
	search_fields = ('name', 'phone', 'service__name', 'service_code')
	list_filter = ('service', 'timestamp')
