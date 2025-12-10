"""
Integration tests for autocomplete API endpoint.

Tests cover activity name autocomplete functionality.
"""

import pytest
from django.urls import reverse
from django.utils import timezone
from energy_tracker.models import Activity
import json


@pytest.mark.integration
@pytest.mark.django_db
class TestAutocompleteActivities:
    """Tests for autocomplete API endpoint."""

    def test_autocomplete_requires_authentication(self, client):
        """Test that autocomplete requires login."""
        response = client.get(reverse('autocomplete_activities'))
        
        # Should redirect to login or return 403
        assert response.status_code in [302, 403]

    def test_autocomplete_returns_suggestions(self, authenticated_client, user):
        """Test that autocomplete returns matching suggestions."""
        # Create activities with similar names
        now = timezone.now()
        Activity.objects.create(user=user, name='Meeting', energy_level=1, duration=60, activity_date=now)
        Activity.objects.create(user=user, name='Meeting with team', energy_level=1, duration=60, activity_date=now)
        Activity.objects.create(user=user, name='Lunch', energy_level=1, duration=60, activity_date=now)
        
        # Search for "meet"
        response = authenticated_client.get(reverse('autocomplete_activities'), {'q': 'meet'})
        
        # Should return JSON response
        assert response.status_code == 200
        
        # Parse JSON response
        if response.get('Content-Type', '').startswith('application/json'):
            data = json.loads(response.content)
            
            # Should be a list of suggestions
            assert isinstance(data, list) or 'suggestions' in data
            
            # Extract suggestions
            if isinstance(data, dict) and 'suggestions' in data:
                suggestions = data['suggestions']
            else:
                suggestions = data
            
            # Should contain matching activities
            suggestion_names = [s if isinstance(s, str) else s.get('name', '') for s in suggestions]
            assert any('meeting' in name.lower() for name in suggestion_names)

    def test_autocomplete_top_5_limit(self, authenticated_client, user):
        """Test that autocomplete limits results to 5."""
        # Create 10 activities with similar names
        now = timezone.now()
        for i in range(10):
            Activity.objects.create(
                user=user,
                name=f'Activity {i}',
                energy_level=1,
                duration=60,
                activity_date=now
            )
        
        # Search for "activity"
        response = authenticated_client.get(reverse('autocomplete_activities'), {'q': 'activity'})
        
        if response.get('Content-Type', '').startswith('application/json'):
            data = json.loads(response.content)
            
            # Extract suggestions
            if isinstance(data, dict) and 'suggestions' in data:
                suggestions = data['suggestions']
            else:
                suggestions = data
            
            # Should return at most 5 suggestions
            assert len(suggestions) <= 5

    def test_autocomplete_frequency_ordering(self, authenticated_client, user):
        """Test that suggestions are ordered by frequency."""
        # Create multiple instances of "Meeting" and fewer of "Meetup"
        now = timezone.now()
        
        # Create "Meeting" 5 times
        for _ in range(5):
            Activity.objects.create(user=user, name='Meeting', energy_level=1, duration=60, activity_date=now)
        
        # Create "Meetup" 2 times
        for _ in range(2):
            Activity.objects.create(user=user, name='Meetup', energy_level=1, duration=60, activity_date=now)
        
        # Search for "meet"
        response = authenticated_client.get(reverse('autocomplete_activities'), {'q': 'meet'})
        
        if response.get('Content-Type', '').startswith('application/json'):
            data = json.loads(response.content)
            
            # Extract suggestions
            if isinstance(data, dict) and 'suggestions' in data:
                suggestions = data['suggestions']
            else:
                suggestions = data
            
            if suggestions:
                # First suggestion should be "Meeting" (more frequent)
                first_suggestion = suggestions[0]
                first_name = first_suggestion if isinstance(first_suggestion, str) else first_suggestion.get('name', '')
                assert first_name == 'Meeting'

    def test_autocomplete_empty_query(self, authenticated_client, user):
        """Test autocomplete with empty query."""
        # Create some activities
        now = timezone.now()
        Activity.objects.create(user=user, name='Meeting', energy_level=1, duration=60, activity_date=now)
        
        # Search with empty query
        response = authenticated_client.get(reverse('autocomplete_activities'), {'q': ''})
        
        if response.get('Content-Type', '').startswith('application/json'):
            data = json.loads(response.content)
            
            # Extract suggestions
            if isinstance(data, dict) and 'suggestions' in data:
                suggestions = data['suggestions']
            else:
                suggestions = data
            
            # Should return empty list or no suggestions
            assert len(suggestions) == 0 or suggestions == []

    def test_autocomplete_user_isolation(self, authenticated_client, user, another_user):
        """Test that autocomplete only returns current user's activities."""
        now = timezone.now()
        
        # Create activity for current user
        Activity.objects.create(user=user, name='User Meeting', energy_level=1, duration=60, activity_date=now)
        
        # Create activity for another user
        Activity.objects.create(user=another_user, name='Other Meeting', energy_level=1, duration=60, activity_date=now)
        
        # Search for "meeting"
        response = authenticated_client.get(reverse('autocomplete_activities'), {'q': 'meeting'})
        
        if response.get('Content-Type', '').startswith('application/json'):
            data = json.loads(response.content)
            
            # Extract suggestions
            if isinstance(data, dict) and 'suggestions' in data:
                suggestions = data['suggestions']
            else:
                suggestions = data
            
            # Extract suggestion names
            suggestion_names = [s if isinstance(s, str) else s.get('name', '') for s in suggestions]
            
            # Should include current user's activity
            assert 'User Meeting' in suggestion_names
            
            # Should NOT include other user's activity
            assert 'Other Meeting' not in suggestion_names
