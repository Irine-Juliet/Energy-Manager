"""
Unit tests for energy_tracker models.

This module tests the Activity and UserProfile models in isolation,
including validation, methods, relationships, and signals.
"""

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError
from datetime import timedelta
from energy_tracker.models import Activity, UserProfile


@pytest.mark.django_db
@pytest.mark.unit
class TestActivityModel:
    """Test cases for the Activity model."""

    def test_activity_creation_with_valid_data(self, user):
        """Test creating an activity with all required fields."""
        activity = Activity.objects.create(
            user=user,
            name='Team Meeting',
            description='Weekly team sync',
            energy_level=1,
            duration=60,
            activity_date=timezone.now()
        )
        
        assert activity.name == 'Team Meeting'
        assert activity.description == 'Weekly team sync'
        assert activity.energy_level == 1
        assert activity.duration == 60
        assert activity.user == user
        assert activity.created_at is not None
        assert activity.updated_at is not None

    def test_activity_default_values(self, user):
        """Test activity creation with default values."""
        activity = Activity.objects.create(
            user=user,
            name='Quick Task',
            energy_level=2
        )
        
        assert activity.duration == 60  # Default duration
        assert activity.description == ''  # Default empty description
        assert activity.activity_date is not None

    @pytest.mark.parametrize('energy_level', [-2, -1, 1, 2])
    def test_energy_level_choices_valid(self, user, energy_level):
        """Test all valid energy level choices."""
        activity = Activity.objects.create(
            user=user,
            name='Test Activity',
            energy_level=energy_level,
            duration=30
        )
        
        assert activity.energy_level == energy_level
        activity.full_clean()  # Should not raise ValidationError

    def test_energy_level_invalid_zero(self, user):
        """Test that energy_level=0 is not in valid choices."""
        activity = Activity(
            user=user,
            name='Test Activity',
            energy_level=0,
            duration=30
        )
        
        with pytest.raises(ValidationError):
            activity.full_clean()

    @pytest.mark.parametrize('invalid_level', [-3, 3, 5, -10, 100])
    def test_energy_level_out_of_range(self, user, invalid_level):
        """Test energy levels outside valid range."""
        activity = Activity(
            user=user,
            name='Test Activity',
            energy_level=invalid_level,
            duration=30
        )
        
        with pytest.raises(ValidationError):
            activity.full_clean()

    def test_duration_validation_minimum(self, user):
        """Test duration validation for minimum values."""
        # Valid: duration = 1
        activity_valid = Activity(
            user=user,
            name='Quick Task',
            energy_level=1,
            duration=1
        )
        activity_valid.full_clean()  # Should not raise
        
        # Invalid: duration = 0
        activity_zero = Activity(
            user=user,
            name='Zero Duration',
            energy_level=1,
            duration=0
        )
        with pytest.raises(ValidationError):
            activity_zero.full_clean()
        
        # Invalid: duration = -5
        activity_negative = Activity(
            user=user,
            name='Negative Duration',
            energy_level=1,
            duration=-5
        )
        with pytest.raises(ValidationError):
            activity_negative.full_clean()

    def test_duration_validation_maximum(self, user):
        """Test duration validation for maximum values."""
        # Valid: duration = 1440 (24 hours)
        activity_valid = Activity(
            user=user,
            name='All Day Task',
            energy_level=1,
            duration=1440
        )
        activity_valid.full_clean()  # Should not raise
        
        # Invalid: duration = 1441
        activity_over = Activity(
            user=user,
            name='Over Max',
            energy_level=1,
            duration=1441
        )
        with pytest.raises(ValidationError):
            activity_over.full_clean()
        
        # Invalid: duration = 10000
        activity_way_over = Activity(
            user=user,
            name='Way Over Max',
            energy_level=1,
            duration=10000
        )
        with pytest.raises(ValidationError):
            activity_way_over.full_clean()

    def test_activity_ordering(self, user):
        """Test that activities are ordered by activity_date descending."""
        now = timezone.now()
        
        # Create activities with different dates
        activity1 = Activity.objects.create(
            user=user, name='First', energy_level=1,
            activity_date=now - timedelta(days=5)
        )
        activity2 = Activity.objects.create(
            user=user, name='Second', energy_level=1,
            activity_date=now - timedelta(days=1)
        )
        activity3 = Activity.objects.create(
            user=user, name='Third', energy_level=1,
            activity_date=now
        )
        activity4 = Activity.objects.create(
            user=user, name='Fourth', energy_level=1,
            activity_date=now - timedelta(days=3)
        )
        activity5 = Activity.objects.create(
            user=user, name='Fifth', energy_level=1,
            activity_date=now - timedelta(hours=12)
        )
        
        # Query all activities
        activities = list(Activity.objects.all())
        
        # Assert ordering (most recent first)
        assert activities[0] == activity3  # now
        assert activities[1] == activity5  # 12 hours ago
        assert activities[2] == activity2  # 1 day ago
        assert activities[3] == activity4  # 3 days ago
        assert activities[4] == activity1  # 5 days ago

    def test_str_method(self, user):
        """Test the __str__ method of Activity."""
        activity = Activity.objects.create(
            user=user,
            name='Team Meeting',
            energy_level=1,
            duration=90
        )
        
        str_repr = str(activity)
        assert 'Team Meeting' in str_repr
        assert '1h 30m' in str_repr
        assert 'Somewhat Energizing' in str_repr

    @pytest.mark.parametrize('duration,expected', [
        (60, '1h'),
        (90, '1h 30m'),
        (30, '30m'),
        (0, '0m'),
        (125, '2h 5m'),
        (1, '1m'),
        (120, '2h'),
        (1440, '24h'),
    ])
    def test_get_duration_display(self, user, duration, expected):
        """Test duration display formatting."""
        activity = Activity.objects.create(
            user=user,
            name='Test',
            energy_level=1,
            duration=duration
        )
        
        assert activity.get_duration_display() == expected

    @pytest.mark.parametrize('energy_level,expected_emoji', [
        (-2, '😫'),
        (-1, '😔'),
        (1, '😊'),
        (2, '🚀'),
    ])
    def test_get_energy_emoji(self, user, energy_level, expected_emoji):
        """Test energy emoji mapping."""
        activity = Activity.objects.create(
            user=user,
            name='Test',
            energy_level=energy_level,
            duration=30
        )
        
        assert activity.get_energy_emoji() == expected_emoji

    def test_activity_user_relationship(self, user):
        """Test the foreign key relationship between Activity and User."""
        activity = Activity.objects.create(
            user=user,
            name='Test',
            energy_level=1,
            duration=30
        )
        
        assert activity.user == user
        assert user.activities.count() == 1
        assert user.activities.first() == activity

    def test_cascade_delete_user_activities(self, user):
        """Test that deleting a user cascades to delete their activities."""
        # Create 3 activities for the user
        Activity.objects.create(user=user, name='Activity 1', energy_level=1)
        Activity.objects.create(user=user, name='Activity 2', energy_level=2)
        Activity.objects.create(user=user, name='Activity 3', energy_level=-1)
        
        assert Activity.objects.filter(user=user).count() == 3
        
        # Delete the user
        user_id = user.id
        user.delete()
        
        # Assert all activities are deleted
        assert Activity.objects.filter(user_id=user_id).count() == 0

    def test_activity_timestamps(self, user):
        """Test created_at and updated_at timestamps."""
        activity = Activity.objects.create(
            user=user,
            name='Test',
            energy_level=1,
            duration=30
        )
        
        # Assert timestamps are set
        assert activity.created_at is not None
        assert activity.updated_at is not None
        # Timestamps should be very close (within a second)
        assert abs((activity.created_at - activity.updated_at).total_seconds()) < 1
        
        # Store original timestamps
        original_created = activity.created_at
        original_updated = activity.updated_at
        
        # Update the activity
        import time
        time.sleep(0.01)  # Small delay to ensure different timestamp
        activity.name = 'Updated Test'
        activity.save()
        
        # Refresh from database
        activity.refresh_from_db()
        
        # Assert created_at unchanged, updated_at changed
        assert activity.created_at == original_created
        assert activity.updated_at > original_updated

    def test_activity_description_optional(self, user):
        """Test that description field is optional."""
        # Create without description
        activity1 = Activity.objects.create(
            user=user,
            name='No Description',
            energy_level=1,
            duration=30
        )
        
        assert activity1.description == ''
        
        # Create with description
        activity2 = Activity.objects.create(
            user=user,
            name='With Description',
            energy_level=1,
            duration=30,
            description='This is a test description'
        )
        
        assert activity2.description == 'This is a test description'


@pytest.mark.django_db
@pytest.mark.unit
class TestUserProfileModel:
    """Test cases for the UserProfile model."""

    def test_profile_creation_on_user_signup(self, db):
        """Test that UserProfile is auto-created via signal when user is created."""
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        
        # Assert profile was auto-created
        assert hasattr(user, 'profile')
        assert user.profile is not None
        assert user.profile.theme == UserProfile.THEME_LIGHT
        assert user.profile.notifications is True

    def test_profile_str_method(self, user):
        """Test the __str__ method of UserProfile."""
        profile = user.profile
        str_repr = str(profile)
        
        assert 'testuser' in str_repr
        assert 'Profile' in str_repr

    @pytest.mark.parametrize('theme', ['light', 'dark'])
    def test_theme_choices_valid(self, user, theme):
        """Test valid theme choices."""
        profile = user.profile
        profile.theme = theme
        profile.save()
        
        profile.refresh_from_db()
        assert profile.theme == theme
        profile.full_clean()  # Should not raise

    def test_theme_invalid_choice(self, user):
        """Test that invalid theme choice raises ValidationError."""
        profile = user.profile
        profile.theme = 'invalid_theme'
        
        with pytest.raises(ValidationError):
            profile.full_clean()

    @pytest.mark.parametrize('notifications_value', [True, False])
    def test_notifications_boolean(self, user, notifications_value):
        """Test notifications boolean field."""
        profile = user.profile
        profile.notifications = notifications_value
        profile.save()
        
        profile.refresh_from_db()
        assert profile.notifications == notifications_value

    def test_profile_one_to_one_relationship(self, user):
        """Test the one-to-one relationship between User and UserProfile."""
        profile = user.profile
        
        assert profile.user == user
        assert user.profile == profile

    def test_profile_update(self, user):
        """Test updating profile fields."""
        profile = user.profile
        
        # Change theme
        profile.theme = UserProfile.THEME_DARK
        profile.notifications = False
        profile.save()
        
        # Refresh from database
        profile.refresh_from_db()
        
        assert profile.theme == UserProfile.THEME_DARK
        assert profile.notifications is False

    def test_profile_cascade_delete(self, user):
        """Test that deleting user also deletes profile."""
        profile_id = user.profile.id
        user.delete()
        
        # Assert profile is also deleted
        assert not UserProfile.objects.filter(id=profile_id).exists()

    def test_profile_signal_on_existing_user(self, user):
        """Test that signal recreates profile if it's deleted."""
        # Delete the profile
        user.profile.delete()
        
        # Save the user (triggers signal)
        user.save()
        
        # Profile should be recreated
        user.refresh_from_db()
        assert hasattr(user, 'profile')
        assert user.profile is not None

    def test_default_theme_value(self, db):
        """Test default theme value is THEME_LIGHT."""
        user = User.objects.create_user(
            username='themetest',
            email='theme@example.com',
            password='testpass'
        )
        
        assert user.profile.theme == UserProfile.THEME_LIGHT

    def test_default_notifications_value(self, db):
        """Test default notifications value is True."""
        user = User.objects.create_user(
            username='notiftest',
            email='notif@example.com',
            password='testpass'
        )
        
        assert user.profile.notifications is True
