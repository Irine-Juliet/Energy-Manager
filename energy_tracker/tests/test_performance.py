"""
Performance Tests for Energy Manager Application

Tests database query optimization, response times, and performance
under load to ensure the application remains responsive.
"""

import time
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from energy_tracker.models import Activity


@pytest.mark.performance
@pytest.mark.django_db
class TestPerformanceOptimization:
    """Test suite for performance and optimization checks."""

    def test_homepage_query_count(self, authenticated_client, user):
        """
        Test that homepage loads efficiently with minimal database queries.

        The homepage should use select_related/prefetch_related to avoid N+1 queries.
        Target: <10 database queries regardless of activity count.
        """
        # Create multiple activities to test query optimization
        now = timezone.now()
        for i in range(20):
            Activity.objects.create(
                user=user,
                name=f"Activity {i}",
                energy_level=2 if i % 2 == 0 else -2,
                duration=60,
                activity_date=now - timedelta(hours=i),
            )

        # Use Django's assertNumQueries to count database queries
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as context:
            response = authenticated_client.get(reverse("homepage"))
            assert response.status_code == 200

        # Assert that we use fewer than 10 queries
        # This ensures we're using proper query optimization
        num_queries = len(context.captured_queries)
        assert num_queries < 10, f"Homepage used {num_queries} queries, expected <10"

        # Verify the page still works correctly
        assert "recent_activities" in response.context
        assert "today_avg" in response.context

    def test_dashboard_with_many_activities(self, authenticated_client, user):
        """
        Test dashboard performance with large dataset (1000 activities).

        The dashboard should load analytics and charts in under 1 second
        even with extensive historical data.
        """
        # Create 1000 activities spread over the last 30 days
        now = timezone.now()
        activities = []

        for i in range(1000):
            # Distribute activities across 30 days
            days_ago = i % 30
            hours_ago = i % 24
            activities.append(
                Activity(
                    user=user,
                    name=f"Activity {i % 50}",  # Reuse 50 activity names
                    energy_level=[-2, -1, 1, 2][i % 4],
                    duration=30 + (i % 120),
                    activity_date=now - timedelta(days=days_ago, hours=hours_ago),
                )
            )

        # Bulk create for efficiency
        Activity.objects.bulk_create(activities)

        # Time the dashboard load
        start_time = time.time()
        response = authenticated_client.get(reverse("dashboard"))
        end_time = time.time()

        assert response.status_code == 200

        # Assert loads in under 1 second
        load_time = end_time - start_time
        assert load_time < 1.0, f"Dashboard took {load_time:.2f}s, expected <1s"

        # Verify dashboard data is present
        assert "weekly_data" in response.context
        assert "hourly_avg" in response.context
        assert "draining_activities" in response.context
        assert "energizing_activities" in response.context

    def test_history_pagination_performance(self, authenticated_client, user):
        """
        Test activity history pagination with large dataset.

        First page load should be fast (<500ms) even with thousands of activities.
        """
        # Create 1000 activities
        now = timezone.now()
        activities = []

        for i in range(1000):
            activities.append(
                Activity(
                    user=user,
                    name=f"Activity {i}",
                    energy_level=2 if i % 2 == 0 else -1,
                    duration=60,
                    activity_date=now - timedelta(hours=i),
                )
            )

        Activity.objects.bulk_create(activities)

        # Time the first page load
        start_time = time.time()
        response = authenticated_client.get(reverse("activity_history"))
        end_time = time.time()

        assert response.status_code == 200

        # Assert loads in under 500ms
        load_time = end_time - start_time
        assert load_time < 0.5, f"History page took {load_time:.2f}s, expected <0.5s"

        # Verify pagination is working
        assert "page_obj" in response.context
        page_obj = response.context["page_obj"]

        # Should have pagination with this many activities
        assert page_obj.paginator.num_pages > 1

        # First page should have the configured page size (typically 20)
        assert len(page_obj.object_list) <= 20

    def test_autocomplete_response_time(self, authenticated_client, user):
        """
        Test autocomplete API response time with many unique activities.

        Autocomplete should respond quickly (<200ms) to provide good UX.
        """
        # Create 100 unique activity names with varying prefixes
        activities = []
        prefixes = ["Meeting", "Exercise", "Work", "Study", "Break"]

        for i in range(100):
            prefix = prefixes[i % len(prefixes)]
            activities.append(
                Activity(
                    user=user,
                    name=f"{prefix} {i}",
                    energy_level=1,
                    duration=60,
                    activity_date=timezone.now() - timedelta(hours=i),
                )
            )

        Activity.objects.bulk_create(activities)

        # Time the autocomplete API call
        start_time = time.time()
        response = authenticated_client.get(
            reverse("autocomplete_activities"), {"q": "meet"}
        )
        end_time = time.time()

        assert response.status_code == 200

        # Assert responds in under 200ms
        response_time = end_time - start_time
        assert (
            response_time < 0.2
        ), f"Autocomplete took {response_time:.2f}s, expected <0.2s"

        # Verify response format
        data = response.json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

        # Should return limited results (typically 5)
        assert len(data["suggestions"]) <= 5

    def test_bulk_delete_performance(self, authenticated_client, user):
        """
        Test bulk delete operation performance with 100 activities.

        Bulk operations should be efficient, completing in under 1 second.
        """
        # Create 100 activities
        activities = []
        now = timezone.now()

        for i in range(100):
            activities.append(
                Activity(
                    user=user,
                    name=f"Activity {i}",
                    energy_level=1,
                    duration=60,
                    activity_date=now - timedelta(hours=i),
                )
            )

        Activity.objects.bulk_create(activities)

        # Get IDs of first 50 activities to delete
        activity_ids = list(
            Activity.objects.filter(user=user)[:50].values_list("id", flat=True)
        )

        # Time the bulk delete operation
        start_time = time.time()
        response = authenticated_client.post(
            reverse("bulk_delete_activities"), {"activity_ids": activity_ids}
        )
        end_time = time.time()

        # Accept both redirect and success status
        assert response.status_code in [200, 302]

        # Assert completes in under 1 second
        operation_time = end_time - start_time
        assert (
            operation_time < 1.0
        ), f"Bulk delete took {operation_time:.2f}s, expected <1s"

        # Verify the activities were actually deleted
        remaining_count = Activity.objects.filter(user=user).count()
        assert (
            remaining_count == 50
        ), f"Expected 50 remaining activities, found {remaining_count}"
