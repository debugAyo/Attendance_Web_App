from django import forms
from .models import SchoolClass, Attendance
from django.contrib.auth.models import User
from django.utils import timezone

class AttendanceForm(forms.Form):
    service = forms.ModelChoiceField(queryset=SchoolClass.objects.all(), label="School Class")
    date = forms.DateField(initial=timezone.now, widget=forms.SelectDateWidget, label="Date")
    attendees = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Present Members"
    )
