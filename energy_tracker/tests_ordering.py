"""
Unit tests for activity ordering behavior.

These tests verify that activities are displayed in the correct order
based on activity_date (when they occurred), not created_at (when they were logged).
"""

from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import timedelta
from .models import Activity


class ActivityOrderingTestCase(TestCase):
    """Test cases for verifying correct activity ordering across all views"""
    
    def setUp(self):
        """Set up test user and client"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_homepage_shows_recent_activities_by_activity_date(self):
        """
        Test that homepage shows activities ordered by activity_date, not created_at.
        
        This is the primary bug fix: when users log activities retrospectively
        (e.g., log breakfast at noon), the homepage should show the 5 most recent
        activities by when they occurred, not by when they were logged.
        """
        now = timezone.now()
        
        # Log 6 activities at different times throughout the day
        for i in range(6):
            Activity.objects.create(
                user=self.user,
                name=f'Activity {i}',
                energy_level=1,
                activity_date=now - timedelta(hours=i),
                duration=60
            )
        
        # Log an activity at an earlier time (8 hours ago) but NOW
        early_activity = Activity.objects.create(
            user=self.user,
            name='Early Morning Activity',
            energy_level=1,
            activity_date=now - timedelta(hours=8),
            duration=60
        )
        
        # Check homepage
        response = self.client.get(reverse('homepage'))
        
        # Verify activities are in the response
        self.assertEqual(response.status_code, 200)
        recent_activities = response.context['recent_activities']
        
        # Should have exactly 5 activities (homepage limit)
        self.assertEqual(len(recent_activities), 5)
        
        # Get activity dates from the response
        dates = [a.activity_date for a in recent_activities]
        
        # Dates should be in descending order (most recent first)
        self.assertEqual(dates, sorted(dates, reverse=True))
        
        # Most recent activity should be first
        self.assertEqual(recent_activities[0].activity_date, now)
        
        # The early morning activity should NOT be in the top 5
        # because it's the 7th most recent (8 hours ago)
        activity_ids = [a.id for a in recent_activities]
        self.assertNotIn(early_activity.id, activity_ids)
    
    def test_history_page_consistent_ordering(self):
        """
        Test that history page shows activities in consistent chronological order.
        
        Activities should be ordered by activity_date descending (most recent first)
        regardless of when they were logged.
        """
        now = timezone.now()
        
        # Create activities at different times
        activities = []
        for i in range(10):
            activity = Activity.objects.create(
                user=self.user,
                name=f'Activity {i}',
                energy_level=1,
                activity_date=now - timedelta(hours=i),
                duration=60
            )
            activities.append(activity)
        
        # Check history page (day view)
        response = self.client.get(reverse('activity_history') + '?view=day')
        
        self.assertEqual(response.status_code, 200)
        page_activities = list(response.context['page_obj'])
        
        # All activities should be present
        self.assertEqual(len(page_activities), 10)
        
        # Verify ordering: most recent first
        dates = [a.activity_date for a in page_activities]
        self.assertEqual(dates, sorted(dates, reverse=True))
    
    def test_dashboard_recent_activities_ordered(self):
        """
        Test that dashboard shows recent activities in correct order.
        
        The dashboard should show the 5 most recent activities from today,
        ordered by activity_date descending.
        """
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Create activities throughout the day
        for i in range(7):
            Activity.objects.create(
                user=self.user,
                name=f'Activity {i}',
                energy_level=1,
                activity_date=today_start + timedelta(hours=i),
                duration=60
            )
        
        # Check dashboard
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        recent_activities = response.context['recent_activities']
        
        # Should have exactly 5 activities
        self.assertEqual(len(recent_activities), 5)
        
        # Should be ordered by activity_date descending
        dates = [a.activity_date for a in recent_activities]
        self.assertEqual(dates, sorted(dates, reverse=True))
        
        # The 5 most recent should be the last 5 hours
        expected_hours = [6, 5, 4, 3, 2]
        actual_hours = [a.activity_date.hour for a in recent_activities]
        self.assertEqual(actual_hours, expected_hours)
    
    def test_retrospective_logging_scenario(self):
        """
        Test realistic scenario: user logs activities throughout the day,
        then remembers to log an earlier activity.
        
        This simulates the exact bug scenario described in the root cause analysis.
        """
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # User logs activities throughout the day
        activities_logged = []
        
        # 9:00 AM - Logs "Morning Meeting" at 9:00 AM
        act1 = Activity.objects.create(
            user=self.user,
            name='Morning Meeting',
            energy_level=-1,
            activity_date=today_start + timedelta(hours=9),
            duration=60
        )
        activities_logged.append(act1)
        
        # 10:00 AM - Logs "Coffee Break" at 10:00 AM
        act2 = Activity.objects.create(
            user=self.user,
            name='Coffee Break',
            energy_level=1,
            activity_date=today_start + timedelta(hours=10),
            duration=30
        )
        activities_logged.append(act2)
        
        # Continue logging activities throughout the day
        for hour in [11, 12, 13, 14]:
            act = Activity.objects.create(
                user=self.user,
                name=f'Activity at {hour}:00',
                energy_level=1,
                activity_date=today_start + timedelta(hours=hour),
                duration=60
            )
            activities_logged.append(act)
        
        # NOW: User realizes they forgot to log breakfast at 8:00 AM
        breakfast = Activity.objects.create(
            user=self.user,
            name='Breakfast',
            energy_level=2,
            activity_date=today_start + timedelta(hours=8),  # Earlier time
            duration=30
        )
        
        # Check homepage
        response = self.client.get(reverse('homepage'))
        recent_activities = list(response.context['recent_activities'])
        
        # Should show exactly 5 activities
        self.assertEqual(len(recent_activities), 5)
        
        # Should be the 5 most recent by activity_date (14:00, 13:00, 12:00, 11:00, 10:00)
        expected_hours = [14, 13, 12, 11, 10]
        actual_hours = [a.activity_date.hour for a in recent_activities]
        self.assertEqual(actual_hours, expected_hours)
        
        # Breakfast (8:00) and Morning Meeting (9:00) should NOT be in top 5
        activity_names = [a.name for a in recent_activities]
        self.assertNotIn('Breakfast', activity_names)
        self.assertNotIn('Morning Meeting', activity_names)
        
        # But they should appear in history page
        response_history = self.client.get(reverse('activity_history') + '?view=day')
        all_activities = list(response_history.context['page_obj'])
        all_names = [a.name for a in all_activities]
        
        self.assertIn('Breakfast', all_names)
        self.assertIn('Morning Meeting', all_names)
        
        # History should show all 7 activities in correct order
        self.assertEqual(len(all_activities), 7)
        history_dates = [a.activity_date for a in all_activities]
        self.assertEqual(history_dates, sorted(history_dates, reverse=True))
    
    def test_activities_with_same_hour_different_minutes(self):
        """
        Test that activities within the same hour are correctly ordered.
        """
        now = timezone.now()
        base_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Create activities at 10:00, 10:15, 10:30, 10:45
        times = [0, 15, 30, 45]
        for minutes in times:
            Activity.objects.create(
                user=self.user,
                name=f'Activity at 10:{minutes:02d}',
                energy_level=1,
                activity_date=base_time + timedelta(minutes=minutes),
                duration=10
            )
        
        # Check homepage
        response = self.client.get(reverse('homepage'))
        recent_activities = list(response.context['recent_activities'])
        
        # Should be ordered with 10:45 first, then 10:30, 10:15, 10:00
        if len(recent_activities) >= 4:
            minutes_list = [a.activity_date.minute for a in recent_activities[:4]]
            self.assertEqual(minutes_list, [45, 30, 15, 0])
    
    def test_empty_state_no_activities(self):
        """
        Test that views handle empty state correctly (no activities).
        """
        # Homepage with no activities
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['recent_activities']), 0)
        self.assertIsNone(response.context['today_avg'])
        
        # Dashboard with no activities
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['recent_activities']), 0)
    
    def test_ordering_with_filters(self):
        """
        Test that ordering is maintained when filters are applied in history view.
        """
        now = timezone.now()
        
        # Create mix of energizing and draining activities
        for i in range(5):
            Activity.objects.create(
                user=self.user,
                name=f'Energizing {i}',
                energy_level=2,
                activity_date=now - timedelta(hours=i),
                duration=60
            )
            Activity.objects.create(
                user=self.user,
                name=f'Draining {i}',
                energy_level=-2,
                activity_date=now - timedelta(hours=i, minutes=30),
                duration=60
            )
        
        # Filter for energizing activities only
        response = self.client.get(reverse('activity_history') + '?energy=2&view=day')
        filtered_activities = list(response.context['page_obj'])
        
        # Should have 5 energizing activities
        self.assertEqual(len(filtered_activities), 5)
        
        # All should be energizing
        for activity in filtered_activities:
            self.assertEqual(activity.energy_level, 2)
        
        # Should still be ordered by activity_date descending
        dates = [a.activity_date for a in filtered_activities]
        self.assertEqual(dates, sorted(dates, reverse=True))
