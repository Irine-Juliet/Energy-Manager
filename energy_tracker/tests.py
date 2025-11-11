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
            'energy_level': '1',
            'activity_date': future_str,
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
            'description': 'Had lunch with team',
            'energy_level': '1',
            # leave activity_date blank so view uses timezone.now()
        })
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        from energy_tracker.models import Activity
        self.assertTrue(Activity.objects.filter(user=self.user, name='Lunch').exists())
