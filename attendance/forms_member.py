from django import forms
from .models import SchoolClass

class MemberAttendanceForm(forms.Form):
    name = forms.CharField(
        label="Full Name", 
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    phone = forms.CharField(
        label="Phone Number", 
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    service_code = forms.CharField(
        label="Class Code", 
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter code displayed at class'})
    )
    service = forms.ModelChoiceField(
        queryset=SchoolClass.objects.all(), 
        label="School Class", 
        required=True,
        empty_label="-- Select a class --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
