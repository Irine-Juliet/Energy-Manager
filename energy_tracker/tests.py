from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

# Avoid importing forms/models at module import time to prevent Django app
# registration issues when the workspace/module path contains characters that
# influence module names. Import inside tests instead.


class ActivityFormTests(TestCase):
    def test_rejects_future_activity_date(self):
        from energy_tracker.forms import ActivityForm
        future = timezone.now() + timedelta(days=1)
        # datetime-local format: YYYY-MM-DDTHH:MM
        future_str = future.strftime('%Y-%m-%dT%H:%M')
        form = ActivityForm(data={
            'name': 'Future Test',
            'energy_level': '-2',
            'activity_date': future_str,
            'duration_hours': '1',
            'duration_minutes': '30',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('activity_date', form.errors)


class LogActivityViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')

    def test_post_creates_activity_and_redirects(self):
        self.client.login(username='tester', password='pass')
        url = reverse('log_activity')
        response = self.client.post(url, data={
            'name': 'Lunch',
            'energy_level': '1',
            'duration_hours': '1',
            'duration_minutes': '0',
            # leave activity_date blank so view uses timezone.now()
        })
        # Should redirect to log_activity page (after success)
        self.assertEqual(response.status_code, 302)
        from energy_tracker.models import Activity
        self.assertTrue(Activity.objects.filter(user=self.user, name='Lunch').exists())


class DashboardHoursPerCategoryTests(TestCase):
    """Tests for the dashboard hour counting fix - verifies duration aggregation"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.login(username='tester', password='pass')
    
    def test_dashboard_hours_per_category_sums_duration(self):
        """Verify that hours_per_category sums actual activity durations"""
        import json
        from energy_tracker.models import Activity
        
        # Create activities with known durations
        Activity.objects.create(
            user=self.user,
            name="Long work session",
            duration=180,  # 3 hours
            energy_level=2,
            activity_date=timezone.now()
        )
        Activity.objects.create(
            user=self.user,
            name="Quick break",
            duration=15,  # 0.25 hours
            energy_level=-1,
            activity_date=timezone.now()
        )
        
        response = self.client.get(reverse('dashboard'))
        hours_data = json.loads(response.context['hours_per_category'])
        
        self.assertEqual(hours_data['2'], 3.0)
        self.assertEqual(hours_data['-1'], 0.25)
    
    def test_dashboard_aggregates_multiple_activities_same_level(self):
        """Verify that multiple activities with same energy level are summed"""
        import json
        from energy_tracker.models import Activity
        
        # Create 3 activities with energy level 2
        for i in range(3):
            Activity.objects.create(
                user=self.user,
                name=f"Activity {i}",
                duration=60,  # 1 hour each
                energy_level=2,
                activity_date=timezone.now()
            )
        
        response = self.client.get(reverse('dashboard'))
        hours_data = json.loads(response.context['hours_per_category'])
        
        self.assertEqual(hours_data['2'], 3.0)  # 3 hours total
    
    def test_dashboard_handles_multiple_activities_same_hour(self):
        """Verify correct behavior when multiple activities occur in same hour"""
        import json
        from energy_tracker.models import Activity
        
        now = timezone.now()
        
        # Two activities in the same hour (9 AM)
        Activity.objects.create(
            user=self.user,
            name="Activity 1",
            duration=120,  # 2 hours
            energy_level=2,
            activity_date=now.replace(hour=9, minute=0)
        )
        Activity.objects.create(
            user=self.user,
            name="Activity 2",
            duration=30,  # 0.5 hours
            energy_level=-2,
            activity_date=now.replace(hour=9, minute=30)
        )
        
        response = self.client.get(reverse('dashboard'))
        hours_data = json.loads(response.context['hours_per_category'])
        
        self.assertEqual(hours_data['2'], 2.0)
        self.assertEqual(hours_data['-2'], 0.5)
    
    def test_dashboard_with_no_activities(self):
        """Verify that all categories show 0 when no activities exist"""
        import json
        
        response = self.client.get(reverse('dashboard'))
        hours_data = json.loads(response.context['hours_per_category'])
        
        for category in ['-2', '-1', '0', '1', '2']:
            self.assertEqual(hours_data[category], 0)
    
    def test_dashboard_with_very_short_duration(self):
        """Test activities with very short durations (1-5 minutes)"""
        import json
        from energy_tracker.models import Activity
        
        Activity.objects.create(
            user=self.user,
            name="Very short activity",
            duration=4,  # 4 minutes
            energy_level=-2,
            activity_date=timezone.now()
        )
        
        response = self.client.get(reverse('dashboard'))
        hours_data = json.loads(response.context['hours_per_category'])
        
        # Should be rounded to 2 decimal places: 4/60 = 0.0666... ≈ 0.07
        self.assertEqual(hours_data['-2'], 0.07)
    
    def test_dashboard_with_very_long_duration(self):
        """Test activities with very long durations (6-8 hours)"""
        import json
        from energy_tracker.models import Activity
        
        Activity.objects.create(
            user=self.user,
            name="Very long activity",
            duration=480,  # 8 hours
            energy_level=1,
            activity_date=timezone.now()
        )
        
        response = self.client.get(reverse('dashboard'))
        hours_data = json.loads(response.context['hours_per_category'])
        
        self.assertEqual(hours_data['1'], 8.0)
    
    def test_dashboard_only_shows_today_activities(self):
        """Verify that only today's activities are counted"""
        import json
        from energy_tracker.models import Activity
        
        # Activity from today
        Activity.objects.create(
            user=self.user,
            name="Today activity",
            duration=60,
            energy_level=2,
            activity_date=timezone.now()
        )
        
        # Activity from yesterday
        yesterday = timezone.now() - timedelta(days=1)
        Activity.objects.create(
            user=self.user,
            name="Yesterday activity",
            duration=120,
            energy_level=2,
            activity_date=yesterday
        )
        
        response = self.client.get(reverse('dashboard'))
        hours_data = json.loads(response.context['hours_per_category'])
        
        # Should only count today's 1 hour, not yesterday's 2 hours
        self.assertEqual(hours_data['2'], 1.0)
