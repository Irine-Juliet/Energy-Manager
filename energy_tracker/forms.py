from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Activity


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
