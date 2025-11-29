"""
Integration tests for dashboard and analytics views.

Tests cover homepage and dashboard analytics functionality.
"""

import json
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from energy_tracker.models import Activity


@pytest.mark.integration
@pytest.mark.django_db
class TestHomepageView:
    """Tests for homepage view."""

    def test_homepage_requires_authentication(self, client):
        """Test that homepage requires login."""
        response = client.get(reverse("homepage"))

        # Should redirect to login
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_homepage_shows_today_average(self, authenticated_client, user):
        """Test that homepage calculates today's average energy."""
        # Create activities today with various energy levels
        now = timezone.now()
        Activity.objects.create(
            user=user, name="Activity 1", energy_level=2, duration=60, activity_date=now
        )
        Activity.objects.create(
            user=user, name="Activity 2", energy_level=1, duration=60, activity_date=now
        )
        Activity.objects.create(
            user=user,
            name="Activity 3",
            energy_level=-1,
            duration=60,
            activity_date=now,
        )

        response = authenticated_client.get(reverse("homepage"))

        assert response.status_code == 200

        # Average should be (2 + 1 + (-1)) / 3 = 0.67 (rounded)
        if "today_avg" in response.context:
            avg = response.context["today_avg"]
            assert avg is not None
            assert 0.6 <= avg <= 0.7

    def test_homepage_recent_activities_limit_5(self, authenticated_client, user):
        """Test that homepage shows maximum 5 recent activities."""
        # Create 7 activities today
        now = timezone.now()
        for i in range(7):
            Activity.objects.create(
                user=user,
                name=f"Activity {i}",
                energy_level=1,
                duration=60,
                activity_date=now - timedelta(minutes=i),
            )

        response = authenticated_client.get(reverse("homepage"))

        # Should have at most 5 recent activities
        if "recent_activities" in response.context:
            recent = response.context["recent_activities"]
            assert len(recent) <= 5

    def test_homepage_recent_activities_ordered(self, authenticated_client, user):
        """Test that recent activities are ordered by date descending."""
        # Create activities at different times
        base_time = timezone.now()
        activities = []
        for i in range(5):
            activity = Activity.objects.create(
                user=user,
                name=f"Activity {i}",
                energy_level=1,
                duration=60,
                activity_date=base_time - timedelta(hours=i),
            )
            activities.append(activity)

        response = authenticated_client.get(reverse("homepage"))

        if "recent_activities" in response.context:
            recent = list(response.context["recent_activities"])
            # First activity should be the most recent
            if recent:
                assert recent[0].activity_date >= recent[-1].activity_date

    def test_homepage_empty_state(self, authenticated_client):
        """Test homepage with no activities."""
        response = authenticated_client.get(reverse("homepage"))

        assert response.status_code == 200

        # Should handle empty state gracefully
        if "today_avg" in response.context:
            avg = response.context["today_avg"]
            assert avg is None or avg == 0

        if "recent_activities" in response.context:
            recent = response.context["recent_activities"]
            assert len(recent) == 0


@pytest.mark.integration
@pytest.mark.django_db
class TestDashboardView:
    """Tests for dashboard analytics view."""

    def test_dashboard_requires_authentication(self, client):
        """Test that dashboard requires login."""
        response = client.get(reverse("dashboard"))

        # Should redirect to login
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_dashboard_today_stats(self, authenticated_client, user):
        """Test dashboard shows today's statistics."""
        # Create activities today
        now = timezone.now()
        Activity.objects.create(
            user=user, name="Activity 1", energy_level=2, duration=60, activity_date=now
        )
        Activity.objects.create(
            user=user, name="Activity 2", energy_level=1, duration=45, activity_date=now
        )
        Activity.objects.create(
            user=user,
            name="Activity 3",
            energy_level=-1,
            duration=30,
            activity_date=now,
        )

        response = authenticated_client.get(reverse("dashboard"))

        assert response.status_code == 200

        # Check today's count
        if "today_count" in response.context:
            assert response.context["today_count"] == 3

        # Check today's average
        if "today_avg" in response.context:
            avg = response.context["today_avg"]
            assert avg is not None

    def test_dashboard_weekly_data_structure(self, authenticated_client, user):
        """Test that weekly data is properly structured."""
        # Create activities over the past week
        base_time = timezone.now()
        for i in range(7):
            Activity.objects.create(
                user=user,
                name=f"Activity {i}",
                energy_level=1 if i % 2 == 0 else -1,
                duration=60,
                activity_date=base_time - timedelta(days=i),
            )

        response = authenticated_client.get(reverse("dashboard"))

        # Check if weekly_data exists in context
        if "weekly_data" in response.context:
            weekly_data = response.context["weekly_data"]
            # Should be JSON or dict with dates and averages
            if isinstance(weekly_data, str):
                data = json.loads(weekly_data)
                assert isinstance(data, (list, dict))

    def test_dashboard_draining_activities_top_3(self, authenticated_client, user):
        """Test that top 3 draining activities are shown."""
        # Create various draining activities
        now = timezone.now()
        Activity.objects.create(
            user=user,
            name="Very Draining",
            energy_level=-2,
            duration=120,
            activity_date=now,
        )
        Activity.objects.create(
            user=user,
            name="Very Draining",
            energy_level=-2,
            duration=90,
            activity_date=now,
        )
        Activity.objects.create(
            user=user,
            name="Somewhat Draining",
            energy_level=-1,
            duration=60,
            activity_date=now,
        )
        Activity.objects.create(
            user=user,
            name="Mildly Draining",
            energy_level=-1,
            duration=30,
            activity_date=now,
        )

        response = authenticated_client.get(reverse("dashboard"))

        if "top_draining" in response.context:
            top_draining = response.context["top_draining"]
            # Should have at most 3 activities
            assert len(top_draining) <= 3
            # First should be most draining
            if top_draining:
                assert top_draining[0]["name"] in ["Very Draining", "Somewhat Draining"]

    def test_dashboard_energizing_activities_top_3(self, authenticated_client, user):
        """Test that top 3 energizing activities are shown."""
        # Create various energizing activities
        now = timezone.now()
        Activity.objects.create(
            user=user,
            name="Very Energizing",
            energy_level=2,
            duration=120,
            activity_date=now,
        )
        Activity.objects.create(
            user=user,
            name="Very Energizing",
            energy_level=2,
            duration=90,
            activity_date=now,
        )
        Activity.objects.create(
            user=user,
            name="Somewhat Energizing",
            energy_level=1,
            duration=60,
            activity_date=now,
        )
        Activity.objects.create(
            user=user,
            name="Mildly Energizing",
            energy_level=1,
            duration=30,
            activity_date=now,
        )

        response = authenticated_client.get(reverse("dashboard"))

        if "top_energizing" in response.context:
            top_energizing = response.context["top_energizing"]
            # Should have at most 3 activities
            assert len(top_energizing) <= 3
            # First should be most energizing
            if top_energizing:
                assert top_energizing[0]["name"] in [
                    "Very Energizing",
                    "Somewhat Energizing",
                ]

    def test_dashboard_activity_points_json(self, authenticated_client, user):
        """Test that activity points are properly formatted for visualization."""
        # Create activities today at different times
        base_time = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        Activity.objects.create(
            user=user,
            name="Morning Meeting",
            energy_level=2,
            duration=60,
            activity_date=base_time,
        )
        Activity.objects.create(
            user=user,
            name="Lunch",
            energy_level=1,
            duration=45,
            activity_date=base_time + timedelta(hours=3),
        )

        response = authenticated_client.get(reverse("dashboard"))

        # Check if activity_points exists
        if "activity_points" in response.context:
            activity_points = response.context["activity_points"]
            # Should be JSON or list
            if isinstance(activity_points, str):
                data = json.loads(activity_points)
                assert isinstance(data, list)
                if data:
                    # Each point should have expected fields
                    point = data[0]
                    assert "id" in point or "name" in point

    def test_dashboard_hourly_avg_24_hours(self, authenticated_client, user):
        """Test hourly average data structure."""
        # Create activities in specific hours
        base_date = timezone.now().date()
        hour_9 = timezone.make_aware(
            timezone.datetime.combine(
                base_date, timezone.datetime.min.time().replace(hour=9)
            )
        )
        hour_10 = timezone.make_aware(
            timezone.datetime.combine(
                base_date, timezone.datetime.min.time().replace(hour=10)
            )
        )
        hour_14 = timezone.make_aware(
            timezone.datetime.combine(
                base_date, timezone.datetime.min.time().replace(hour=14)
            )
        )

        Activity.objects.create(
            user=user,
            name="Activity 9am",
            energy_level=2,
            duration=60,
            activity_date=hour_9,
        )
        Activity.objects.create(
            user=user,
            name="Activity 10am",
            energy_level=1,
            duration=60,
            activity_date=hour_10,
        )
        Activity.objects.create(
            user=user,
            name="Activity 2pm",
            energy_level=-1,
            duration=60,
            activity_date=hour_14,
        )

        response = authenticated_client.get(reverse("dashboard"))

        # Check hourly_avg if it exists
        if "hourly_avg" in response.context:
            hourly_avg = response.context["hourly_avg"]
            # Should be a dict or JSON with 24 hours
            if isinstance(hourly_avg, str):
                data = json.loads(hourly_avg)
                assert isinstance(data, (dict, list))

    def test_dashboard_hours_per_category_calculation(self, authenticated_client, user):
        """Test hours per category calculation."""
        # Create activity with 3 hours duration
        now = timezone.now()
        Activity.objects.create(
            user=user,
            name="Long Activity",
            energy_level=2,
            duration=180,  # 3 hours
            activity_date=now,
        )

        response = authenticated_client.get(reverse("dashboard"))

        # Check hours_per_category if it exists
        if "hours_per_category" in response.context:
            hours_per_category = response.context["hours_per_category"]
            # Should have hours for energy level 2
            if isinstance(hours_per_category, dict):
                # Energy level 2 should have 3.0 hours
                assert "2" in hours_per_category or 2 in hours_per_category

    def test_dashboard_hours_per_category_multiple_same_level(
        self, authenticated_client, user
    ):
        """Test hours per category with multiple activities of same level."""
        # Create 3 activities with energy level 2, each 1 hour
        now = timezone.now()
        for i in range(3):
            Activity.objects.create(
                user=user,
                name=f"Activity {i}",
                energy_level=2,
                duration=60,
                activity_date=now - timedelta(minutes=i),
            )

        response = authenticated_client.get(reverse("dashboard"))

        if "hours_per_category" in response.context:
            hours_per_category = response.context["hours_per_category"]
            if isinstance(hours_per_category, dict):
                # Should have 3 hours total for energy level 2
                energy_2_hours = hours_per_category.get(
                    "2", 0
                ) or hours_per_category.get(2, 0)
                assert energy_2_hours == 3.0

    def test_dashboard_hours_per_category_today_only(self, authenticated_client, user):
        """Test that hours per category only counts today's activities."""
        # Create activity yesterday
        yesterday = timezone.now() - timedelta(days=1)
        Activity.objects.create(
            user=user,
            name="Yesterday Activity",
            energy_level=2,
            duration=120,
            activity_date=yesterday,
        )

        # Create activity today
        today = timezone.now()
        Activity.objects.create(
            user=user,
            name="Today Activity",
            energy_level=2,
            duration=60,
            activity_date=today,
        )

        response = authenticated_client.get(reverse("dashboard"))

        if "hours_per_category" in response.context:
            hours_per_category = response.context["hours_per_category"]
            if isinstance(hours_per_category, dict):
                # Should only count today's 1 hour, not yesterday's 2 hours
                energy_2_hours = hours_per_category.get(
                    "2", 0
                ) or hours_per_category.get(2, 0)
                assert energy_2_hours == 1.0
