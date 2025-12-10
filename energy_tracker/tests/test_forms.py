"""
Unit tests for energy_tracker forms.

This module tests form validation, cleaning methods, and widget configurations
for ActivityForm, SignUpForm, and SettingsForm.
"""

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from energy_tracker.forms import ActivityForm, SignUpForm, SettingsForm
from energy_tracker.models import Activity, UserProfile


@pytest.mark.django_db
@pytest.mark.unit
class TestActivityForm:
    """Test cases for the ActivityForm."""

    def test_valid_form_all_fields(self, user):
        """Test form with all valid fields."""
        form_data = {
            'name': 'Team Meeting',
            'energy_level': 1,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 2,
            'duration_minutes': 30,
        }
        
        form = ActivityForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"
        assert form.cleaned_data['duration'] == 150  # 2h 30m

    def test_valid_form_minimum_required(self, user):
        """Test form with only required fields."""
        form_data = {
            'name': 'Quick Task',
            'energy_level': 2,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 0,
            'duration_minutes': 15,
        }
        
        form = ActivityForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_name_required(self):
        """Test that name field is required."""
        form_data = {
            'name': '',
            'energy_level': 1,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 1,
            'duration_minutes': 0,
        }
        
        form = ActivityForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_name_max_length(self):
        """Test name field maximum length validation."""
        # Valid: exactly 100 characters
        form_data_valid = {
            'name': 'A' * 100,
            'energy_level': 1,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 1,
            'duration_minutes': 0,
        }
        form_valid = ActivityForm(data=form_data_valid)
        assert form_valid.is_valid(), f"Form errors: {form_valid.errors}"
        
        # Invalid: 101 characters
        form_data_invalid = {
            'name': 'A' * 101,
            'energy_level': 1,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 1,
            'duration_minutes': 0,
        }
        form_invalid = ActivityForm(data=form_data_invalid)
        assert not form_invalid.is_valid()
        assert 'name' in form_invalid.errors

    def test_name_whitespace_only(self):
        """Test that name with only whitespace is invalid."""
        form_data = {
            'name': '   ',
            'energy_level': 1,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 1,
            'duration_minutes': 0,
        }
        
        form = ActivityForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_energy_level_required(self):
        """Test that energy_level is required."""
        form_data = {
            'name': 'Test Activity',
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 1,
            'duration_minutes': 0,
        }
        
        form = ActivityForm(data=form_data)
        assert not form.is_valid()
        assert 'energy_level' in form.errors

    @pytest.mark.parametrize('energy_level', [-2, -1, 1, 2])
    def test_energy_level_valid_choices(self, energy_level):
        """Test all valid energy level choices."""
        form_data = {
            'name': 'Test Activity',
            'energy_level': energy_level,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 1,
            'duration_minutes': 0,
        }
        
        form = ActivityForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"

    @pytest.mark.parametrize('invalid_level', [0, 3, -3, 'invalid'])
    def test_energy_level_invalid_choices(self, invalid_level):
        """Test invalid energy level choices."""
        form_data = {
            'name': 'Test Activity',
            'energy_level': invalid_level,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 1,
            'duration_minutes': 0,
        }
        
        form = ActivityForm(data=form_data)
        assert not form.is_valid()
        assert 'energy_level' in form.errors

    @pytest.mark.parametrize('hours', [0, 1, 12, 23, 24])
    def test_duration_hours_valid(self, hours):
        """Test valid duration hours."""
        form_data = {
            'name': 'Test Activity',
            'energy_level': 1,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': hours,
            'duration_minutes': 0,
        }
        
        form = ActivityForm(data=form_data)
        # Only valid if total duration >= 1 minute
        if hours > 0:
            assert form.is_valid(), f"Form errors: {form.errors}"
        else:
            # 0 hours, 0 minutes = invalid
            assert not form.is_valid()

    @pytest.mark.parametrize('hours', [-1, 25, 100])
    def test_duration_hours_out_of_range(self, hours):
        """Test duration hours outside valid range."""
        form_data = {
            'name': 'Test Activity',
            'energy_level': 1,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': hours,
            'duration_minutes': 0,
        }
        
        form = ActivityForm(data=form_data)
        assert not form.is_valid()

    @pytest.mark.parametrize('minutes', [0, 30, 59])
    def test_duration_minutes_valid(self, minutes):
        """Test valid duration minutes."""
        form_data = {
            'name': 'Test Activity',
            'energy_level': 1,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 1,
            'duration_minutes': minutes,
        }
        
        form = ActivityForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"

    @pytest.mark.parametrize('minutes', [-1, 60, 100])
    def test_duration_minutes_out_of_range(self, minutes):
        """Test duration minutes outside valid range."""
        form_data = {
            'name': 'Test Activity',
            'energy_level': 1,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 1,
            'duration_minutes': minutes,
        }
        
        form = ActivityForm(data=form_data)
        assert not form.is_valid()

    @pytest.mark.parametrize('hours,minutes,expected_duration', [
        (2, 30, 150),
        (0, 15, 15),
        (1, 0, 60),
        (3, 45, 225),
        (24, 0, 1440),
    ])
    def test_duration_calculation_combined(self, hours, minutes, expected_duration):
        """Test duration calculation from hours and minutes."""
        form_data = {
            'name': 'Test Activity',
            'energy_level': 1,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': hours,
            'duration_minutes': minutes,
        }
        
        form = ActivityForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"
        assert form.cleaned_data['duration'] == expected_duration

    def test_minimum_duration_validation(self):
        """Test that activity must be at least 1 minute."""
        form_data = {
            'name': 'Test Activity',
            'energy_level': 1,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 0,
            'duration_minutes': 0,
        }
        
        form = ActivityForm(data=form_data)
        assert not form.is_valid()
        assert '__all__' in form.errors or 'duration_hours' in form.errors or 'duration_minutes' in form.errors
        error_messages = str(form.errors)
        assert 'at least 1 minute' in error_messages.lower()

    def test_maximum_duration_validation(self):
        """Test that activity cannot exceed 24 hours."""
        form_data = {
            'name': 'Test Activity',
            'energy_level': 1,
            'activity_date': timezone.now().isoformat(),
            'duration_hours': 24,
            'duration_minutes': 1,  # 1441 minutes total
        }
        
        form = ActivityForm(data=form_data)
        assert not form.is_valid()
        error_messages = str(form.errors)
        assert '24 hours' in error_messages or 'exceed' in error_messages.lower()

    def test_activity_date_in_past(self):
        """Test that past dates are valid."""
        past_date = timezone.now() - timedelta(days=1)
        form_data = {
            'name': 'Yesterday Activity',
            'energy_level': 1,
            'activity_date': past_date.isoformat(),
            'duration_hours': 1,
            'duration_minutes': 0,
        }
        
        form = ActivityForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_activity_date_current(self):
        """Test that current date/time is valid."""
        now = timezone.now()
        form_data = {
            'name': 'Current Activity',
            'energy_level': 1,
            'activity_date': now.isoformat(),
            'duration_hours': 1,
            'duration_minutes': 0,
        }
        
        form = ActivityForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_activity_date_future(self):
        """Test that future dates are rejected."""
        future_date = timezone.now() + timedelta(days=1)
        form_data = {
            'name': 'Future Activity',
            'energy_level': 1,
            'activity_date': future_date.isoformat(),
            'duration_hours': 1,
            'duration_minutes': 0,
        }
        
        form = ActivityForm(data=form_data)
        assert not form.is_valid()
        assert 'activity_date' in form.errors
        error_message = str(form.errors['activity_date'])
        assert 'future' in error_message.lower()

    def test_form_initial_values_on_edit(self, user):
        """Test that form initializes with correct duration values when editing."""
        # Create an activity with 2h 30m duration (150 minutes)
        activity = Activity.objects.create(
            user=user,
            name='Existing Activity',
            energy_level=1,
            duration=150,
            activity_date=timezone.now()
        )
        
        # Initialize form with the activity instance
        form = ActivityForm(instance=activity)
        
        # Check initial values
        assert form.fields['duration_hours'].initial == 2
        assert form.fields['duration_minutes'].initial == 30

    def test_form_widgets_and_attributes(self):
        """Test that form widgets have correct CSS classes and attributes."""
        form = ActivityForm()
        
        # Test name field widget
        name_widget = form.fields['name'].widget
        assert 'class' in name_widget.attrs
        assert 'autocomplete' in name_widget.attrs
        assert name_widget.attrs['autocomplete'] == 'off'
        
        # Test energy_level is hidden
        energy_widget = form.fields['energy_level'].widget
        assert energy_widget.input_type == 'hidden'


@pytest.mark.django_db
@pytest.mark.unit
class TestSignUpForm:
    """Test cases for the SignUpForm."""

    def test_valid_signup_form(self):
        """Test form with all valid signup data."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        
        form = SignUpForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_passwords_must_match(self):
        """Test that password1 and password2 must match."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass456!',
        }
        
        form = SignUpForm(data=form_data)
        assert not form.is_valid()
        assert 'password2' in form.errors

    def test_email_required(self):
        """Test that email is required."""
        form_data = {
            'username': 'newuser',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        
        form = SignUpForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_email_format_validation(self):
        """Test email format validation."""
        # Valid email
        form_data_valid = {
            'username': 'newuser',
            'email': 'user@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        form_valid = SignUpForm(data=form_data_valid)
        assert form_valid.is_valid(), f"Form errors: {form_valid.errors}"
        
        # Invalid emails
        invalid_emails = ['notanemail', 'missing@domain', '@nodomain.com', 'spaces in@email.com']
        for invalid_email in invalid_emails:
            form_data_invalid = {
                'username': 'newuser',
                'email': invalid_email,
                'password1': 'ComplexPass123!',
                'password2': 'ComplexPass123!',
            }
            form_invalid = SignUpForm(data=form_data_invalid)
            assert not form_invalid.is_valid(), f"Email '{invalid_email}' should be invalid"

    def test_username_already_exists(self):
        """Test that duplicate username is rejected."""
        # Create existing user
        User.objects.create_user(username='existinguser', email='existing@example.com', password='testpass')
        
        # Try to sign up with same username
        form_data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        
        form = SignUpForm(data=form_data)
        assert not form.is_valid()
        assert 'username' in form.errors

    def test_password_strength_requirements(self):
        """Test that weak passwords are rejected by Django validators."""
        # Weak password: too short and common
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': '123',
            'password2': '123',
        }
        
        form = SignUpForm(data=form_data)
        assert not form.is_valid()
        assert 'password2' in form.errors or 'password1' in form.errors

    def test_form_widget_classes(self):
        """Test that form fields have correct Tailwind CSS classes."""
        form = SignUpForm()
        
        # Check that fields have CSS classes
        assert 'class' in form.fields['email'].widget.attrs
        assert 'class' in form.fields['password1'].widget.attrs
        assert 'class' in form.fields['password2'].widget.attrs


@pytest.mark.django_db
@pytest.mark.unit
class TestSettingsForm:
    """Test cases for the SettingsForm."""

    def test_valid_settings_form(self, user):
        """Test form with valid settings data."""
        form_data = {
            'theme': 'dark',
            'notifications': False,
        }
        
        form = SettingsForm(data=form_data, instance=user.profile)
        assert form.is_valid(), f"Form errors: {form.errors}"

    @pytest.mark.parametrize('theme', ['light', 'dark'])
    def test_theme_choices(self, user, theme):
        """Test valid theme choices."""
        form_data = {
            'theme': theme,
            'notifications': True,
        }
        
        form = SettingsForm(data=form_data, instance=user.profile)
        assert form.is_valid(), f"Form errors: {form.errors}"
        
        # Test invalid theme
        form_data_invalid = {
            'theme': 'invalid_theme',
            'notifications': True,
        }
        form_invalid = SettingsForm(data=form_data_invalid, instance=user.profile)
        assert not form_invalid.is_valid()
        assert 'theme' in form_invalid.errors

    @pytest.mark.parametrize('notifications_value', [True, False])
    def test_notifications_boolean(self, user, notifications_value):
        """Test notifications boolean field."""
        form_data = {
            'theme': 'light',
            'notifications': notifications_value,
        }
        
        form = SettingsForm(data=form_data, instance=user.profile)
        assert form.is_valid(), f"Form errors: {form.errors}"
