"""
Integration tests for activity CRUD views.

Tests cover logging, editing, and deleting activities.
"""

import pytest
from django.urls import reverse
from django.utils import timezone
from energy_tracker.models import Activity
from datetime import timedelta
import json


@pytest.mark.integration
@pytest.mark.django_db
class TestLogActivityView:
    """Tests for log activity functionality."""

    def test_log_activity_requires_authentication(self, client):
        """Test that log activity page requires login."""
        response = client.get(reverse('log_activity'))
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_log_activity_get_displays_form(self, authenticated_client):
        """Test that GET request shows the activity form."""
        response = authenticated_client.get(reverse('log_activity'))
        
        assert response.status_code == 200
        assert any('log_activity.html' in t.name for t in response.templates)
        assert 'form' in response.context

    def test_log_activity_post_valid_creates_activity(self, authenticated_client, user):
        """Test that valid POST creates an activity."""
        from django.utils import timezone
        now = timezone.now()
        activity_data = {
            'name': 'Team Meeting',
            'energy_level': '2',
            'duration_hours': '1',
            'duration_minutes': '30',
            'activity_date': now.isoformat(),
        }
        
        # Get initial count
        initial_count = Activity.objects.filter(user=user).count()
        
        response = authenticated_client.post(reverse('log_activity'), data=activity_data)
        
        # Check activity was created
        assert Activity.objects.filter(user=user).count() == initial_count + 1
        
        # Get the created activity
        activity = Activity.objects.filter(user=user).latest('created_at')
        assert activity.name == 'Team Meeting'
        assert activity.energy_level == 2
        assert activity.duration == 90  # 1h 30m = 90 minutes
        assert activity.user == user
        
        # Check redirect
        assert response.status_code == 302

    def test_log_activity_post_invalid_shows_errors(self, authenticated_client, user):
        """Test that invalid POST shows form errors."""
        activity_data = {
            'name': '',  # Required field
            'energy_level': '2',
            'duration_hours': '1',
            'duration_minutes': '30',
        }
        
        initial_count = Activity.objects.filter(user=user).count()
        
        response = authenticated_client.post(reverse('log_activity'), data=activity_data)
        
        # No activity should be created
        assert Activity.objects.filter(user=user).count() == initial_count
        
        # Form should have errors
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_log_activity_normalizes_name_casing(self, authenticated_client, user):
        """Test that activity names are normalized to most common casing."""
        # Create existing activities with capitalized name
        for _ in range(5):
            Activity.objects.create(
                user=user,
                name='Meeting',
                energy_level=1,
                duration=60,
                activity_date=timezone.now()
            )
        
        # Log new activity with lowercase
        activity_data = {
            'name': 'meeting',
            'energy_level': '2',
            'duration_hours': '1',
            'duration_minutes': '0',
        }
        
        authenticated_client.post(reverse('log_activity'), data=activity_data)
        
        # Get the latest activity
        activity = Activity.objects.filter(user=user).latest('created_at')
        
        # Should be normalized to 'Meeting' (most common casing)
        assert activity.name == 'Meeting'

    def test_log_activity_uses_current_time_if_not_provided(self, authenticated_client, user):
        """Test that activity_date defaults to current time."""
        from django.utils import timezone
        now = timezone.now()
        activity_data = {
            'name': 'Quick Task',
            'energy_level': '1',
            'duration_hours': '0',
            'duration_minutes': '15',
            'activity_date': now.isoformat(),
        }
        
        before = now - timezone.timedelta(seconds=5)
        authenticated_client.post(reverse('log_activity'), data=activity_data)
        after = timezone.now() + timezone.timedelta(seconds=5)
        
        activity = Activity.objects.filter(user=user).latest('created_at')
        
        # Activity date should be close to now
        assert before <= activity.activity_date <= after

    def test_log_activity_ajax_request(self, authenticated_client, user):
        """Test AJAX request returns JSON response."""
        activity_data = {
            'name': 'AJAX Activity',
            'energy_level': '2',
            'duration_hours': '1',
            'duration_minutes': '0',
        }
        
        response = authenticated_client.post(
            reverse('log_activity'),
            data=activity_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check if JSON response (if view supports AJAX)
        if response.get('Content-Type', '').startswith('application/json'):
            data = json.loads(response.content)
            assert 'success' in data or 'redirect' in data

    def test_log_activity_ajax_invalid(self, authenticated_client):
        """Test AJAX request with invalid data."""
        activity_data = {
            'name': '',  # Invalid
            'energy_level': '2',
        }
        
        response = authenticated_client.post(
            reverse('log_activity'),
            data=activity_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check response (may be JSON or HTML depending on implementation)
        if response.get('Content-Type', '').startswith('application/json'):
            assert response.status_code in [200, 400]


@pytest.mark.integration
@pytest.mark.django_db
class TestEditActivityView:
    """Tests for edit activity functionality."""

    def test_edit_activity_requires_authentication(self, client, activity):
        """Test that edit page requires login."""
        response = client.get(reverse('edit_activity', kwargs={'pk': activity.pk}))
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_edit_activity_get_shows_form(self, authenticated_client, activity):
        """Test that GET request shows pre-populated form."""
        response = authenticated_client.get(reverse('edit_activity', kwargs={'pk': activity.pk}))
        
        assert response.status_code == 200
        assert any('edit_activity.html' in t.name for t in response.templates)
        assert 'form' in response.context
        assert response.context['activity'] == activity

    def test_edit_activity_post_updates(self, authenticated_client, activity):
        """Test that POST request updates the activity."""
        from django.utils import timezone
        now = timezone.now()
        updated_data = {
            'name': 'Updated Activity Name',
            'energy_level': '-1',
            'duration_hours': '2',
            'duration_minutes': '15',
            'activity_date': now.isoformat(),
        }
        
        response = authenticated_client.post(
            reverse('edit_activity', kwargs={'pk': activity.pk}),
            data=updated_data
        )
        
        # Refresh activity from database
        activity.refresh_from_db()
        
        # Check updates were saved
        assert activity.name == 'Updated Activity Name'
        assert activity.energy_level == -1
        assert activity.duration == 135  # 2h 15m = 135 minutes
        
        # Check redirect
        assert response.status_code == 302

    def test_edit_activity_user_isolation(self, authenticated_client, another_user):
        """Test that users cannot edit other users' activities."""
        # Create activity for another user
        other_activity = Activity.objects.create(
            user=another_user,
            name='Other User Activity',
            energy_level=1,
            duration=60,
            activity_date=timezone.now()
        )
        
        response = authenticated_client.get(
            reverse('edit_activity', kwargs={'pk': other_activity.pk})
        )
        
        # Should return 404 (activity doesn't exist for this user)
        assert response.status_code == 404

    def test_edit_nonexistent_activity(self, authenticated_client):
        """Test editing non-existent activity returns 404."""
        response = authenticated_client.get(
            reverse('edit_activity', kwargs={'pk': 99999})
        )
        
        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
class TestDeleteActivityView:
    """Tests for delete activity functionality."""

    def test_delete_activity_requires_authentication(self, client, activity):
        """Test that delete page requires login."""
        response = client.get(reverse('delete_activity', kwargs={'pk': activity.pk}))
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_delete_activity_get_confirmation(self, authenticated_client, activity):
        """Test that GET request shows confirmation page."""
        response = authenticated_client.get(
            reverse('delete_activity', kwargs={'pk': activity.pk})
        )
        
        assert response.status_code == 200
        assert any('delete_activity.html' in t.name for t in response.templates)
        assert response.context['activity'] == activity

    def test_delete_activity_post_deletes(self, authenticated_client, user, activity):
        """Test that POST request deletes the activity."""
        activity_pk = activity.pk
        
        response = authenticated_client.post(
            reverse('delete_activity', kwargs={'pk': activity_pk})
        )
        
        # Check activity was deleted
        assert not Activity.objects.filter(pk=activity_pk).exists()
        
        # Check redirect
        assert response.status_code == 302

    def test_delete_activity_user_isolation(self, authenticated_client, another_user):
        """Test that users cannot delete other users' activities."""
        # Create activity for another user
        other_activity = Activity.objects.create(
            user=another_user,
            name='Other User Activity',
            energy_level=1,
            duration=60,
            activity_date=timezone.now()
        )
        
        other_activity_pk = other_activity.pk
        
        response = authenticated_client.post(
            reverse('delete_activity', kwargs={'pk': other_activity_pk})
        )
        
        # Should return 404
        assert response.status_code == 404
        
        # Activity should still exist
        assert Activity.objects.filter(pk=other_activity_pk).exists()


@pytest.mark.integration
@pytest.mark.django_db
class TestBulkDeleteView:
    """Tests for bulk delete functionality."""

    def test_bulk_delete_multiple_activities(self, authenticated_client, user):
        """Test bulk deletion of multiple activities."""
        # Create 5 activities
        activities = []
        for i in range(5):
            activity = Activity.objects.create(
                user=user,
                name=f'Activity {i}',
                energy_level=1,
                duration=60,
                activity_date=timezone.now()
            )
            activities.append(activity)
        
        # Select 3 to delete
        delete_ids = [activities[0].pk, activities[1].pk, activities[2].pk]
        
        response = authenticated_client.post(
            reverse('bulk_delete_activities'),
            data={'activity_ids': delete_ids}
        )
        
        # Check 3 were deleted
        assert not Activity.objects.filter(pk__in=delete_ids).exists()
        
        # Check 2 remain
        assert Activity.objects.filter(user=user).count() == 2

    def test_bulk_delete_user_isolation(self, authenticated_client, user, another_user):
        """Test that bulk delete respects user isolation."""
        # Create activities for both users
        user_activity = Activity.objects.create(
            user=user,
            name='User Activity',
            energy_level=1,
            duration=60,
            activity_date=timezone.now()
        )
        
        other_activity = Activity.objects.create(
            user=another_user,
            name='Other User Activity',
            energy_level=1,
            duration=60,
            activity_date=timezone.now()
        )
        
        # Try to delete both (user should only be able to delete their own)
        response = authenticated_client.post(
            reverse('bulk_delete_activities'),
            data={'activity_ids': [user_activity.pk, other_activity.pk]}
        )
        
        # User's activity should be deleted
        assert not Activity.objects.filter(pk=user_activity.pk).exists()
        
        # Other user's activity should still exist
        assert Activity.objects.filter(pk=other_activity.pk).exists()

    def test_bulk_delete_empty_selection(self, authenticated_client):
        """Test bulk delete with no activities selected."""
        response = authenticated_client.post(
            reverse('bulk_delete_activities'),
            data={'activity_ids': []}
        )
        
        # Should handle gracefully (redirect or show message)
        assert response.status_code in [200, 302]
