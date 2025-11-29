"""
Unit tests for energy_tracker utility functions.

This module tests the utility functions in utils.py, particularly
the get_canonical_activity_name function for name normalization.
"""

import pytest
from django.utils import timezone

from energy_tracker.models import Activity
from energy_tracker.utils import get_canonical_activity_name


@pytest.mark.django_db
@pytest.mark.unit
class TestGetCanonicalActivityName:
    """Test cases for the get_canonical_activity_name utility function."""

    def test_no_existing_activities_returns_input(self, user):
        """Test that function returns input when user has no activities."""
        result = get_canonical_activity_name(user, "Meeting")
        assert result == "Meeting"

    def test_exact_match_returns_input(self, user):
        """Test that exact match returns the same casing."""
        # Create activity with exact casing
        Activity.objects.create(user=user, name="Meeting", energy_level=1, duration=60)

        result = get_canonical_activity_name(user, "Meeting")
        assert result == "Meeting"

    def test_case_insensitive_match_single(self, user):
        """Test case-insensitive matching with single activity."""
        # Create activity with capitalized name
        Activity.objects.create(user=user, name="Meeting", energy_level=1, duration=60)

        # Query with lowercase
        result = get_canonical_activity_name(user, "meeting")
        assert result == "Meeting"

    def test_case_insensitive_match_multiple_same_count(self, user):
        """Test when multiple casings have same count."""
        # Create 1 activity with 'Meeting'
        Activity.objects.create(
            user=user,
            name="Meeting",
            energy_level=1,
            duration=60,
            activity_date=timezone.now(),
        )

        # Create 1 activity with 'meeting'
        Activity.objects.create(
            user=user,
            name="meeting",
            energy_level=1,
            duration=60,
            activity_date=timezone.now(),
        )

        # Query with uppercase
        result = get_canonical_activity_name(user, "MEETING")

        # Should return one of them (implementation returns most common or most recent)
        assert result in ["Meeting", "meeting"]

    def test_returns_most_common_casing(self, user):
        """Test that most common casing is returned."""
        # Create 5 activities with 'Meeting'
        for _ in range(5):
            Activity.objects.create(
                user=user, name="Meeting", energy_level=1, duration=60
            )

        # Create 2 activities with 'meeting'
        for _ in range(2):
            Activity.objects.create(
                user=user, name="meeting", energy_level=1, duration=60
            )

        # Query with uppercase
        result = get_canonical_activity_name(user, "MEETING")

        # Should return 'Meeting' (count=5)
        assert result == "Meeting"

    def test_whitespace_trimmed(self, user):
        """Test that whitespace is trimmed from input."""
        # Create activity
        Activity.objects.create(user=user, name="Meeting", energy_level=1, duration=60)

        # Query with whitespace
        result = get_canonical_activity_name(user, "  Meeting  ")
        assert result == "Meeting"

    def test_different_users_isolated(self, user, another_user):
        """Test that activities are isolated between users."""
        # User A has 'Meeting' (capitalized)
        Activity.objects.create(user=user, name="Meeting", energy_level=1, duration=60)

        # User B has 'meeting' (lowercase)
        Activity.objects.create(
            user=another_user, name="meeting", energy_level=1, duration=60
        )

        # Query for User B with uppercase
        result = get_canonical_activity_name(another_user, "MEETING")

        # Should return User B's version
        assert result == "meeting"

    def test_empty_string_input(self, user):
        """Test behavior with empty string input."""
        result = get_canonical_activity_name(user, "")
        assert result == ""

    def test_special_characters_in_name(self, user):
        """Test names with special characters."""
        # Create activity with special characters
        Activity.objects.create(
            user=user, name="Team Meeting #1", energy_level=1, duration=60
        )

        # Query with different casing
        result = get_canonical_activity_name(user, "team meeting #1")
        assert result == "Team Meeting #1"

    def test_unicode_characters(self, user):
        """Test names with unicode characters."""
        # Create activity with unicode
        Activity.objects.create(
            user=user, name="Café Break", energy_level=1, duration=60
        )

        # Query with different casing
        result = get_canonical_activity_name(user, "café break")
        assert result == "Café Break"
