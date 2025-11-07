from django import forms
from .models import ChurchService

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
        label="Service Code", 
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter code displayed at service'})
    )
    service = forms.ModelChoiceField(
        queryset=ChurchService.objects.all(), 
        label="Church Service", 
        required=True,
        empty_label="-- Select a service --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
