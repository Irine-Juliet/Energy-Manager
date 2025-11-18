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
    activity_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        }),
        required=False,
        help_text='Leave blank to use current time'
    )
    
    class Meta:
        model = Activity
        fields = ['name', 'description', 'energy_level', 'activity_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'e.g., Team Meeting'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'Optional: Add details about this activity'
            }),
            'energy_level': forms.RadioSelect(),
        }
        labels = {
            'name': 'Activity Name',
            'description': 'Description (optional)',
            'energy_level': 'How did this make you feel?',
            'activity_date': 'When did this happen?',
        }

    def clean(self):
        """Form-level validation: no future activity_date, name required, energy range check."""
        cleaned = super().clean()
        activity_date = cleaned.get('activity_date')
        name = cleaned.get('name')
        energy = cleaned.get('energy_level')

        # Name required (Model has no blank restriction beyond CharField, keep explicit)
        if not name:
            raise ValidationError({'name': 'Please enter an activity name.'})

        # If a date was provided, ensure it's not in the future
        if activity_date:
            # make aware if naive and USE_TZ is enabled
            try:
                now = timezone.now()
                if activity_date > now:
                    raise ValidationError({'activity_date': 'Activity date cannot be in the future.'})
            except TypeError:
                # In case of unexpected types, let field-level validators handle it
                pass

        # Energy level must be in allowed range
        if energy is None or not (-2 <= int(energy) <= 2):
            raise ValidationError({'energy_level': 'Invalid energy value.'})

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
