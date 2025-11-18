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
