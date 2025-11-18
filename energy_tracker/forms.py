from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Activity
from django.core.exceptions import ValidationError
from django.utils import timezone
from django import forms
from .models import UserProfile


class SignUpForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            'placeholder': 'Email address'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            'placeholder': 'Confirm password'
        })


class ActivityForm(forms.ModelForm):
    """Form for logging activities"""
    duration_hours = forms.IntegerField(
        min_value=0,
        max_value=24,
        initial=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            'id': 'durationHours'
        })
    )
    duration_minutes = forms.IntegerField(
        min_value=0,
        max_value=59,
        initial=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            'id': 'durationMinutes'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing activity, populate duration_hours and duration_minutes
        if self.instance and self.instance.pk and hasattr(self.instance, 'duration'):
            total_minutes = self.instance.duration
            self.fields['duration_hours'].initial = total_minutes // 60
            self.fields['duration_minutes'].initial = total_minutes % 60
    
    class Meta:
        model = Activity
        fields = ['name', 'energy_level', 'activity_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition',
                'placeholder': 'e.g., Team Meeting, Exercise, Coding',
                'maxlength': '100',
                'autocomplete': 'off',
                'id': 'activityName'
            }),
            'energy_level': forms.HiddenInput(attrs={
                'id': 'energy_level'
            }),
            'activity_date': forms.HiddenInput(attrs={
                'id': 'activity_date'
            }),
        }
        labels = {
            'name': 'Activity Name',
            'energy_level': 'Energy Impact',
        }

    def clean_name(self):
        """Validate activity name"""
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('Activity name is required.')
        if len(name) > 100:
            raise ValidationError('Activity name cannot exceed 100 characters.')
        return name

    def clean_activity_date(self):
        """Ensure activity date is not in the future"""
        activity_date = self.cleaned_data.get('activity_date')
        if activity_date:
            now = timezone.now()
            if activity_date > now:
                raise ValidationError('Cannot log activities in the future.')
        return activity_date

    def clean(self):
        """Form-level validation: duration validation"""
        cleaned = super().clean()
        duration_hours = cleaned.get('duration_hours', 0)
        duration_minutes = cleaned.get('duration_minutes', 0)
        
        # Calculate total duration in minutes
        if duration_hours is None:
            duration_hours = 0
        if duration_minutes is None:
            duration_minutes = 0
            
        total_duration = duration_hours * 60 + duration_minutes
        
        # Validate duration range
        if total_duration < 1:
            raise ValidationError('Activity must be at least 1 minute.')
        if total_duration > 1440:
            raise ValidationError('Activity cannot exceed 24 hours.')
        
        # Store calculated duration for use in view
        cleaned['duration'] = total_duration
        
        return cleaned



class SettingsForm(forms.ModelForm):
    """Form for user settings: theme and notifications."""
    class Meta:
        model = UserProfile
        fields = ['theme', 'notifications']
        widgets = {
            'theme': forms.RadioSelect(choices=UserProfile.THEME_CHOICES),
            'notifications': forms.CheckboxInput(),
        }
        labels = {
            'theme': 'Theme',
            'notifications': 'Notifications',
        }
