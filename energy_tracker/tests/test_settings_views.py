"""
Integration tests for settings and preferences views.

Tests cover user settings and profile management.
"""

import pytest
from django.urls import reverse
from energy_tracker.models import UserProfile


@pytest.mark.integration
@pytest.mark.django_db
class TestSettingsView:
    """Tests for settings view functionality."""

    def test_settings_requires_authentication(self, client):
        """Test that settings page requires login."""
        response = client.get(reverse('settings'))
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_settings_get_displays_form(self, authenticated_client, user):
        """Test that GET request shows settings form."""
        response = authenticated_client.get(reverse('settings'))
        
        assert response.status_code == 200
        assert any('settings.html' in t.name for t in response.templates)
        assert 'form' in response.context

    def test_settings_update_theme(self, authenticated_client, user, profile):
        """Test updating theme setting."""
        # Initial theme should be light
        assert profile.theme == UserProfile.THEME_LIGHT
        
        # Update to dark theme
        settings_data = {
            'theme': UserProfile.THEME_DARK,
            'notifications': profile.notifications,
        }
        
        response = authenticated_client.post(reverse('settings'), data=settings_data)
        
        # Refresh profile from database
        profile.refresh_from_db()
        
        # Check theme was updated
        assert profile.theme == UserProfile.THEME_DARK
        
        # Check for success (redirect or success message)
        assert response.status_code in [200, 302]

    def test_settings_update_notifications(self, authenticated_client, user, profile):
        """Test updating notifications setting."""
        # Initial notifications should be enabled
        assert profile.notifications == True
        
        # Disable notifications
        settings_data = {
            'theme': profile.theme,
            'notifications': False,
        }
        
        response = authenticated_client.post(reverse('settings'), data=settings_data)
        
        # Refresh profile from database
        profile.refresh_from_db()
        
        # Check notifications were updated
        assert profile.notifications == False
        
        # Check for success
        assert response.status_code in [200, 302]

    def test_settings_creates_profile_if_missing(self, authenticated_client, user):
        """Test that settings creates profile if it doesn't exist."""
        # Delete profile if it exists
        UserProfile.objects.filter(user=user).delete()
        
        # Access settings page
        response = authenticated_client.get(reverse('settings'))
        
        assert response.status_code == 200
        
        # Profile should be created (either by signal or view)
        assert UserProfile.objects.filter(user=user).exists()
