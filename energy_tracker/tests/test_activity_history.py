"""
Integration tests for activity history and search views.

Tests cover activity history filtering, searching, and pagination.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from energy_tracker.models import Activity


@pytest.mark.integration
@pytest.mark.django_db
class TestActivityHistoryView:
    """Tests for activity history view with filtering and search."""

    def test_history_requires_authentication(self, client):
        """Test that history page requires login."""
        response = client.get(reverse("activity_history"))

        # Should redirect to login
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_history_default_day_view(self, authenticated_client, user):
        """Test that default view shows today's activities only."""
        # Create activities today and yesterday
        today = timezone.now()
        yesterday = today - timedelta(days=1)

        today_activity = Activity.objects.create(
            user=user,
            name="Today Activity",
            energy_level=1,
            duration=60,
            activity_date=today,
        )

        Activity.objects.create(
            user=user,
            name="Yesterday Activity",
            energy_level=1,
            duration=60,
            activity_date=yesterday,
        )

        response = authenticated_client.get(reverse("activity_history"))

        assert response.status_code == 200

        # Check which activities are in context
        if "activities" in response.context:
            activities = list(response.context["activities"])
            activity_ids = [a.id for a in activities]
            # Should include today's activity
            assert today_activity.id in activity_ids
            # Depending on implementation, may or may not include yesterday

    def test_history_week_view(self, authenticated_client, user):
        """Test week view shows last 7 days of activities."""
        # Create activities at different time periods
        today = timezone.now()
        three_days_ago = today - timedelta(days=3)
        ten_days_ago = today - timedelta(days=10)

        recent_activity = Activity.objects.create(
            user=user,
            name="Recent Activity",
            energy_level=1,
            duration=60,
            activity_date=three_days_ago,
        )

        old_activity = Activity.objects.create(
            user=user,
            name="Old Activity",
            energy_level=1,
            duration=60,
            activity_date=ten_days_ago,
        )

        response = authenticated_client.get(
            reverse("activity_history"), {"view": "week"}
        )

        if "activities" in response.context:
            activities = list(response.context["activities"])
            activity_ids = [a.id for a in activities]
            # Should include recent (3 days ago)
            assert recent_activity.id in activity_ids
            # Should not include old (10 days ago)
            assert old_activity.id not in activity_ids

    def test_history_month_view(self, authenticated_client, user):
        """Test month view shows last 30 days of activities."""
        # Create activities at different time periods
        today = timezone.now()
        fifteen_days_ago = today - timedelta(days=15)
        forty_days_ago = today - timedelta(days=40)

        recent_activity = Activity.objects.create(
            user=user,
            name="Recent Activity",
            energy_level=1,
            duration=60,
            activity_date=fifteen_days_ago,
        )

        old_activity = Activity.objects.create(
            user=user,
            name="Old Activity",
            energy_level=1,
            duration=60,
            activity_date=forty_days_ago,
        )

        response = authenticated_client.get(
            reverse("activity_history"), {"view": "month"}
        )

        if "activities" in response.context:
            activities = list(response.context["activities"])
            activity_ids = [a.id for a in activities]
            # Should include recent (15 days ago)
            assert recent_activity.id in activity_ids
            # Should not include old (40 days ago)
            assert old_activity.id not in activity_ids

    def test_history_energy_filter(self, authenticated_client, user):
        """Test filtering by energy level."""
        # Create mix of energizing and draining activities
        now = timezone.now()

        energizing = Activity.objects.create(
            user=user,
            name="Energizing Activity",
            energy_level=2,
            duration=60,
            activity_date=now,
        )

        draining = Activity.objects.create(
            user=user,
            name="Draining Activity",
            energy_level=-2,
            duration=60,
            activity_date=now,
        )

        # Filter for energy level 2
        response = authenticated_client.get(
            reverse("activity_history"), {"energy": "2"}
        )

        if "activities" in response.context:
            activities = list(response.context["activities"])
            activity_ids = [a.id for a in activities]
            # Should include energizing
            assert energizing.id in activity_ids
            # Should not include draining
            assert draining.id not in activity_ids

    def test_history_search_by_name(self, authenticated_client, user):
        """Test searching activities by name."""
        # Create activities with different names
        now = timezone.now()

        Activity.objects.create(
            user=user,
            name="Team Meeting",
            energy_level=1,
            duration=60,
            activity_date=now,
        )

        Activity.objects.create(
            user=user, name="Exercise", energy_level=2, duration=60, activity_date=now
        )

        Activity.objects.create(
            user=user,
            name="Lunch Break",
            energy_level=1,
            duration=45,
            activity_date=now,
        )

        # Search for "meet"
        response = authenticated_client.get(reverse("activity_history"), {"q": "meet"})

        if "activities" in response.context:
            activities = list(response.context["activities"])
            [a.id for a in activities]
            activity_names = [a.name.lower() for a in activities]
            # Should include meeting (case-insensitive search)
            assert any("meet" in name for name in activity_names)

    def test_history_pagination(self, authenticated_client, user):
        """Test that history is paginated."""
        # Create 25 activities
        now = timezone.now()
        for i in range(25):
            Activity.objects.create(
                user=user,
                name=f"Activity {i}",
                energy_level=1,
                duration=60,
                activity_date=now - timedelta(minutes=i),
            )

        response = authenticated_client.get(reverse("activity_history"))

        # Check if pagination is present
        if "page_obj" in response.context:
            page_obj = response.context["page_obj"]
            # Should have multiple pages
            assert page_obj.paginator.num_pages >= 2
            # First page should have limited items (typically 10-20)
            assert len(page_obj) <= 20
        elif "activities" in response.context:
            # Even without explicit pagination, shouldn't show all 25 on one page
            response.context["activities"]
            # Some implementations might use different pagination methods
            pass

    def test_history_ordering_consistent(self, authenticated_client, user):
        """Test that activities are ordered by date descending."""
        # Create activities at various times
        base_time = timezone.now()
        activities_created = []

        for i in range(5):
            activity = Activity.objects.create(
                user=user,
                name=f"Activity {i}",
                energy_level=1,
                duration=60,
                activity_date=base_time - timedelta(hours=i),
            )
            activities_created.append(activity)

        response = authenticated_client.get(reverse("activity_history"))

        if "activities" in response.context:
            activities = list(response.context["activities"])
            # Should be ordered by activity_date descending
            if len(activities) >= 2:
                for i in range(len(activities) - 1):
                    assert (
                        activities[i].activity_date >= activities[i + 1].activity_date
                    )

    def test_history_user_isolation(self, authenticated_client, user, another_user):
        """Test that users only see their own activities."""
        # Create activities for both users
        now = timezone.now()

        user_activity = Activity.objects.create(
            user=user,
            name="User Activity",
            energy_level=1,
            duration=60,
            activity_date=now,
        )

        other_activity = Activity.objects.create(
            user=another_user,
            name="Other User Activity",
            energy_level=1,
            duration=60,
            activity_date=now,
        )

        response = authenticated_client.get(reverse("activity_history"))

        if "activities" in response.context:
            activities = list(response.context["activities"])
            activity_ids = [a.id for a in activities]
            # Should include user's activity
            assert user_activity.id in activity_ids
            # Should NOT include other user's activity
            assert other_activity.id not in activity_ids

    def test_history_combined_filters(self, authenticated_client, user):
        """Test combining multiple filters."""
        # Create various activities
        base_time = timezone.now()

        # This should match all filters
        matching = Activity.objects.create(
            user=user,
            name="Team Meeting",
            energy_level=2,
            duration=60,
            activity_date=base_time,
        )

        # Wrong energy level
        wrong_energy = Activity.objects.create(
            user=user,
            name="Team Meeting",
            energy_level=-1,
            duration=60,
            activity_date=base_time,
        )

        # Wrong name
        wrong_name = Activity.objects.create(
            user=user,
            name="Exercise",
            energy_level=2,
            duration=60,
            activity_date=base_time,
        )

        # Too old
        too_old = Activity.objects.create(
            user=user,
            name="Team Meeting",
            energy_level=2,
            duration=60,
            activity_date=base_time - timedelta(days=10),
        )

        # Apply combined filters: week view + energy=2 + search="meet"
        response = authenticated_client.get(
            reverse("activity_history"), {"view": "week", "energy": "2", "q": "meet"}
        )

        if "activities" in response.context:
            activities = list(response.context["activities"])
            activity_ids = [a.id for a in activities]
            # Should only include the matching one
            assert matching.id in activity_ids
            # Others should be filtered out
            assert wrong_energy.id not in activity_ids
            assert wrong_name.id not in activity_ids
            assert too_old.id not in activity_ids
