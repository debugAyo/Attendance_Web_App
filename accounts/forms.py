from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(forms.Form):
    ROLE_CHOICES = [
        ("member", "Member"),
        ("admin", "Admin"),
    ]
    GENDER_CHOICES = [
        ("", "Select Gender"),
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]
    HOW_HEARD_CHOICES = [
        ("", "Select an option"),
        ("evangelism", "Evangelism/Street Outreach"),
        ("friend", "Through a Friend/Family Member"),
        ("social_media", "Social Media (Facebook, Instagram, etc.)"),
        ("website", "Church Website"),
        ("passing_by", "Passing By/One-time Visit"),
        ("relocation", "Relocated to the Area"),
        ("invitation", "Invited by Church Member"),
        ("other", "Other"),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))

    # Admin fields
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter admin username"}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter admin email"}))
    password1 = forms.CharField(required=False, widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter password"}))
    password2 = forms.CharField(required=False, widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm password"}))

    # Member fields
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., John Doe"}), label="Full Name")
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., 08012345678"}), label="Phone Number")
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES, 
        required=False, 
        widget=forms.Select(attrs={"class": "form-control"})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="Date of Birth"
    )
    wedding_anniversary = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="Wedding Anniversary"
    )
    member_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "e.g., member@example.com"}),
        label="Email Address"
    )
    
    # First-timer enquiry
    how_heard = forms.ChoiceField(
        choices=HOW_HEARD_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="How did you hear about us?"
    )
    how_heard_other = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Please specify..."}),
        label="If other, please specify"
    )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        if role == 'admin':
            # Require admin fields
            for field in ['username', 'email', 'password1', 'password2']:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for admin registration.')
            if cleaned_data.get('password1') != cleaned_data.get('password2'):
                self.add_error('password2', 'Passwords do not match.')
        elif role == 'member':
            # Require member fields
            for field in ['name', 'phone', 'gender']:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for member registration.')
        return cleaned_data
