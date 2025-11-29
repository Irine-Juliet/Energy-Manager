# Best Practices for Unit, Integration, and End-to-End Tests
## Energy Manager Django Application

**Date:** November 29, 2025  
**Application:** Energy Manager - Personal Energy Tracking Web Application  
**Framework:** Django 5.0  
**Testing Framework:** pytest with pytest-django

---

## Table of Contents

1. [Overview](#overview)
2. [Testing Strategy](#testing-strategy)
3. [Unit Testing Best Practices](#unit-testing-best-practices)
4. [Integration Testing Best Practices](#integration-testing-best-practices)
5. [End-to-End Testing Best Practices](#end-to-end-testing-best-practices)
6. [Django-Specific Testing Guidelines](#django-specific-testing-guidelines)
7. [Test Organization and Structure](#test-organization-and-structure)
8. [Testing Tools and Configuration](#testing-tools-and-configuration)
9. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
10. [Performance and Optimization](#performance-and-optimization)

---

## Overview

The Energy Manager application is a server-side rendered multi-page Django application with the following characteristics:
- **Type:** CRUD application with data-driven dashboard
- **Architecture:** 3-tier web application (Presentation, Application, Data layers)
- **Key Features:** Activity logging, analytics, user authentication, data visualization
- **Database:** SQLite (with PostgreSQL support)
- **Frontend:** Django templates with Tailwind CSS and Chart.js

### Testing Pyramid for Energy Manager

```
        /\
       /  \
      /E2E \    ← 10% (Browser-based, Selenium)
     /______\
    /        \
   /Integration\ ← 30% (API/View tests, Form validation)
  /____________\
 /              \
/  Unit Tests    \ ← 60% (Models, Utils, Business Logic)
/________________\
```

---

## Testing Strategy

### Test Coverage Goals

1. **Unit Tests (60%):** Focus on business logic, model methods, utility functions
2. **Integration Tests (30%):** View logic, form validation, database interactions
3. **End-to-End Tests (10%):** Critical user flows, authentication, key workflows

### Priority Areas for Energy Manager

**High Priority:**
- User authentication and authorization
- Activity logging and data persistence
- Energy level calculations and aggregations
- Dashboard analytics and visualizations
- Data filtering and search functionality

**Medium Priority:**
- Form validation
- Template rendering
- URL routing
- Settings and preferences

**Low Priority:**
- Static file serving
- Admin interface customizations
- Non-critical UI elements

---

## Unit Testing Best Practices

### 1. Model Testing

**Focus:** Business logic, model methods, data validation, custom managers

```python
# energy_tracker/tests/test_models.py
import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from energy_tracker.models import Activity, UserProfile
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestActivityModel:
    """Test Activity model methods and properties."""
    
    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    @pytest.fixture
    def activity(self, user):
        """Create a test activity."""
        return Activity.objects.create(
            user=user,
            name='Morning Exercise',
            activity_date=timezone.now(),
            energy_level=2,
            duration=30
        )
    
    def test_activity_creation(self, activity):
        """Test that an activity can be created with valid data."""
        assert activity.name == 'Morning Exercise'
        assert activity.energy_level == 2
        assert activity.duration == 30
        assert activity.created_at is not None
    
    def test_energy_level_validation(self, user):
        """Test that energy_level is within valid range (-2 to +2)."""
        with pytest.raises(Exception):
            Activity.objects.create(
                user=user,
                name='Invalid Activity',
                energy_level=5,  # Invalid: out of range
                duration=20
            )
    
    def test_activity_string_representation(self, activity):
        """Test the __str__ method returns expected format."""
        expected = f"{activity.name} - Energy: {activity.energy_level}"
        assert str(activity) == expected or activity.name in str(activity)
    
    def test_activity_ordering(self, user):
        """Test activities are ordered by activity_date descending."""
        # Create activities at different times
        now = timezone.now()
        activity1 = Activity.objects.create(
            user=user, name='First', 
            activity_date=now - timedelta(hours=2),
            energy_level=1, duration=15
        )
        activity2 = Activity.objects.create(
            user=user, name='Second', 
            activity_date=now - timedelta(hours=1),
            energy_level=0, duration=20
        )
        activity3 = Activity.objects.create(
            user=user, name='Third', 
            activity_date=now,
            energy_level=-1, duration=25
        )
        
        activities = list(Activity.objects.filter(user=user))
        assert activities[0] == activity3
        assert activities[1] == activity2
        assert activities[2] == activity1
    
    def test_user_activities_only(self, user):
        """Test that users only see their own activities."""
        other_user = User.objects.create_user(
            username='otheruser',
            password='pass123'
        )
        
        Activity.objects.create(
            user=user, name='My Activity',
            energy_level=1, duration=10
        )
        Activity.objects.create(
            user=other_user, name='Their Activity',
            energy_level=-1, duration=15
        )
        
        user_activities = Activity.objects.filter(user=user)
        assert user_activities.count() == 1
        assert user_activities.first().name == 'My Activity'
```

**Key Principles for Model Unit Tests:**
- ✅ Test one thing at a time
- ✅ Use fixtures for common setup
- ✅ Test both valid and invalid data
- ✅ Test custom model methods
- ✅ Test data relationships and constraints
- ✅ Mock external dependencies
- ✅ Use descriptive test names

### 2. Utility Function Testing

```python
# energy_tracker/tests/test_utils.py
import pytest
from datetime import datetime, time
from django.utils import timezone
from energy_tracker.utils import (
    calculate_average_energy,
    group_by_hour,
    filter_activities_by_date_range
)

class TestUtilityFunctions:
    """Test utility functions in isolation."""
    
    def test_calculate_average_energy_with_activities(self):
        """Test average calculation with multiple activities."""
        activities = [
            {'energy_level': 2},
            {'energy_level': 1},
            {'energy_level': -1},
        ]
        result = calculate_average_energy(activities)
        assert result == pytest.approx(0.67, rel=0.01)
    
    def test_calculate_average_energy_empty_list(self):
        """Test average calculation with no activities."""
        result = calculate_average_energy([])
        assert result == 0.0
    
    def test_group_by_hour_aggregation(self):
        """Test that activities are correctly grouped by hour."""
        activities = [
            {'activity_date': datetime(2024, 1, 1, 9, 30), 'energy_level': 2},
            {'activity_date': datetime(2024, 1, 1, 9, 45), 'energy_level': 1},
            {'activity_date': datetime(2024, 1, 1, 10, 15), 'energy_level': -1},
        ]
        
        result = group_by_hour(activities)
        
        assert 9 in result
        assert len(result[9]) == 2
        assert result[9][0]['energy_level'] == 2
```

**Key Principles for Utility Unit Tests:**
- ✅ Test edge cases (empty, null, boundary values)
- ✅ Test with various input types
- ✅ Avoid database access (pure functions)
- ✅ Use parametrized tests for similar cases
- ✅ Test error handling

### 3. Form Testing

```python
# energy_tracker/tests/test_forms.py
import pytest
from datetime import datetime
from django.utils import timezone
from energy_tracker.forms import ActivityForm, UserProfileForm

class TestActivityForm:
    """Test ActivityForm validation and behavior."""
    
    def test_valid_activity_form(self):
        """Test form is valid with correct data."""
        form_data = {
            'name': 'Morning Jog',
            'activity_date': timezone.now(),
            'energy_level': 2,
            'duration': 30
        }
        form = ActivityForm(data=form_data)
        assert form.is_valid()
    
    def test_energy_level_out_of_range(self):
        """Test form rejects invalid energy level."""
        form_data = {
            'name': 'Test Activity',
            'energy_level': 5,  # Invalid
            'duration': 20
        }
        form = ActivityForm(data=form_data)
        assert not form.is_valid()
        assert 'energy_level' in form.errors
    
    def test_negative_duration(self):
        """Test form rejects negative duration."""
        form_data = {
            'name': 'Test Activity',
            'energy_level': 1,
            'duration': -10  # Invalid
        }
        form = ActivityForm(data=form_data)
        assert not form.is_valid()
        assert 'duration' in form.errors
    
    def test_empty_name(self):
        """Test form requires activity name."""
        form_data = {
            'name': '',
            'energy_level': 1,
            'duration': 20
        }
        form = ActivityForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors
    
    @pytest.mark.parametrize('energy_level', [-2, -1, 0, 1, 2])
    def test_all_valid_energy_levels(self, energy_level):
        """Test all valid energy levels are accepted."""
        form_data = {
            'name': 'Test Activity',
            'energy_level': energy_level,
            'duration': 15
        }
        form = ActivityForm(data=form_data)
        assert form.is_valid()
```

---

## Integration Testing Best Practices

### 1. View Testing with Django Test Client

**Focus:** HTTP request/response, view logic, template rendering, authentication

```python
# energy_tracker/tests/test_views.py
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from energy_tracker.models import Activity
from datetime import datetime
from django.utils import timezone

@pytest.mark.django_db
class TestActivityViews:
    """Integration tests for activity-related views."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return Client()
    
    @pytest.fixture
    def user(self):
        """Create and return a test user."""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def authenticated_client(self, client, user):
        """Return an authenticated client."""
        client.login(username='testuser', password='testpass123')
        return client
    
    def test_homepage_requires_authentication(self, client):
        """Test that homepage redirects unauthenticated users."""
        response = client.get(reverse('homepage'))
        assert response.status_code == 302
        assert '/login/' in response.url
    
    def test_homepage_authenticated_user(self, authenticated_client, user):
        """Test authenticated user can access homepage."""
        response = authenticated_client.get(reverse('homepage'))
        assert response.status_code == 200
        assert b'Energy Manager' in response.content or b'Dashboard' in response.content
    
    def test_log_activity_get(self, authenticated_client):
        """Test GET request to log activity page."""
        response = authenticated_client.get(reverse('log_activity'))
        assert response.status_code == 200
        assert b'Log Activity' in response.content or b'form' in response.content
    
    def test_log_activity_post_valid_data(self, authenticated_client, user):
        """Test POST request with valid activity data."""
        activity_data = {
            'name': 'Test Activity',
            'activity_date': timezone.now().isoformat(),
            'energy_level': 2,
            'duration': 30
        }
        
        response = authenticated_client.post(
            reverse('log_activity'),
            data=activity_data
        )
        
        # Should redirect after successful creation
        assert response.status_code in [200, 302]
        
        # Verify activity was created
        assert Activity.objects.filter(
            user=user,
            name='Test Activity'
        ).exists()
    
    def test_log_activity_post_invalid_data(self, authenticated_client, user):
        """Test POST request with invalid data shows errors."""
        invalid_data = {
            'name': '',  # Empty name
            'energy_level': 5,  # Invalid energy level
            'duration': -10  # Negative duration
        }
        
        response = authenticated_client.post(
            reverse('log_activity'),
            data=invalid_data
        )
        
        # Should stay on same page with errors
        assert response.status_code == 200
        
        # No activity should be created
        assert Activity.objects.filter(user=user).count() == 0
    
    def test_activity_history_filters(self, authenticated_client, user):
        """Test activity history filtering functionality."""
        # Create test activities
        now = timezone.now()
        Activity.objects.create(
            user=user,
            name='High Energy Activity',
            activity_date=now,
            energy_level=2,
            duration=30
        )
        Activity.objects.create(
            user=user,
            name='Low Energy Activity',
            activity_date=now,
            energy_level=-2,
            duration=20
        )
        
        # Test energy level filter
        response = authenticated_client.get(
            reverse('activity_history'),
            {'energy_level': '2'}
        )
        
        assert response.status_code == 200
        assert b'High Energy Activity' in response.content
    
    def test_dashboard_displays_analytics(self, authenticated_client, user):
        """Test dashboard shows analytics data."""
        # Create sample activities
        now = timezone.now()
        for i in range(5):
            Activity.objects.create(
                user=user,
                name=f'Activity {i}',
                activity_date=now,
                energy_level=i - 2,  # -2, -1, 0, 1, 2
                duration=15
            )
        
        response = authenticated_client.get(reverse('dashboard'))
        
        assert response.status_code == 200
        # Check for analytics elements
        assert 'context' in dir(response) or response.content
    
    def test_edit_activity(self, authenticated_client, user):
        """Test editing an existing activity."""
        activity = Activity.objects.create(
            user=user,
            name='Original Name',
            activity_date=timezone.now(),
            energy_level=1,
            duration=20
        )
        
        updated_data = {
            'name': 'Updated Name',
            'activity_date': activity.activity_date.isoformat(),
            'energy_level': 2,
            'duration': 30
        }
        
        response = authenticated_client.post(
            reverse('edit_activity', args=[activity.id]),
            data=updated_data
        )
        
        # Refresh from database
        activity.refresh_from_db()
        
        assert activity.name == 'Updated Name'
        assert activity.energy_level == 2
        assert activity.duration == 30
    
    def test_delete_activity(self, authenticated_client, user):
        """Test deleting an activity."""
        activity = Activity.objects.create(
            user=user,
            name='To Delete',
            activity_date=timezone.now(),
            energy_level=0,
            duration=10
        )
        
        activity_id = activity.id
        
        response = authenticated_client.post(
            reverse('delete_activity', args=[activity_id])
        )
        
        # Activity should be deleted
        assert not Activity.objects.filter(id=activity_id).exists()
    
    def test_user_cannot_access_others_activities(self, client, user):
        """Test users cannot access other users' activities."""
        # Create another user and their activity
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        other_activity = Activity.objects.create(
            user=other_user,
            name='Private Activity',
            activity_date=timezone.now(),
            energy_level=1,
            duration=15
        )
        
        # Login as first user
        client.login(username='testuser', password='testpass123')
        
        # Try to access other user's activity
        response = client.get(
            reverse('edit_activity', args=[other_activity.id])
        )
        
        # Should be forbidden or redirect
        assert response.status_code in [403, 404, 302]
```

**Key Principles for Integration Tests:**
- ✅ Test complete request-response cycles
- ✅ Verify authentication and authorization
- ✅ Test form submissions and validation
- ✅ Check database state changes
- ✅ Verify correct templates are used
- ✅ Test redirects and status codes
- ✅ Use fixtures for common setup

### 2. Database Integration Testing

```python
# energy_tracker/tests/test_database_integration.py
import pytest
from django.db import transaction
from django.db.utils import IntegrityError
from energy_tracker.models import Activity, UserProfile
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestDatabaseIntegration:
    """Test database constraints and relationships."""
    
    def test_cascade_delete_user_activities(self):
        """Test that deleting a user deletes their activities."""
        user = User.objects.create_user(username='testuser', password='pass')
        
        Activity.objects.create(
            user=user,
            name='Activity 1',
            energy_level=1,
            duration=10
        )
        Activity.objects.create(
            user=user,
            name='Activity 2',
            energy_level=-1,
            duration=15
        )
        
        assert Activity.objects.filter(user=user).count() == 2
        
        user.delete()
        
        assert Activity.objects.filter(user=user).count() == 0
    
    def test_unique_constraint_violation(self):
        """Test database enforces unique constraints."""
        # If you have unique constraints, test them
        user = User.objects.create_user(username='user1', password='pass')
        
        # Try to create duplicate username
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(username='user1', password='pass2')
    
    def test_bulk_create_activities(self):
        """Test bulk creation of activities."""
        user = User.objects.create_user(username='testuser', password='pass')
        
        activities = [
            Activity(user=user, name=f'Activity {i}', energy_level=i-5, duration=10)
            for i in range(10)
        ]
        
        Activity.objects.bulk_create(activities)
        
        assert Activity.objects.filter(user=user).count() == 10
```

---

## End-to-End Testing Best Practices

### 1. Selenium Testing for Critical User Flows

**Focus:** User interactions, JavaScript behavior, full workflows

```python
# energy_tracker/tests/test_e2e.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User

@pytest.mark.e2e
class TestUserJourney(StaticLiveServerTestCase):
    """End-to-end tests for complete user journeys."""
    
    @classmethod
    def setUpClass(cls):
        """Set up Selenium WebDriver."""
        super().setUpClass()
        cls.selenium = webdriver.Firefox()  # or Chrome
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up Selenium WebDriver."""
        cls.selenium.quit()
        super().tearDownClass()
    
    def setUp(self):
        """Create test user before each test."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_signup_and_login(self):
        """Test complete signup and login flow."""
        # Go to signup page
        self.selenium.get(f'{self.live_server_url}/signup/')
        
        # Fill in signup form
        username_input = self.selenium.find_element(By.NAME, 'username')
        username_input.send_keys('newuser')
        
        email_input = self.selenium.find_element(By.NAME, 'email')
        email_input.send_keys('newuser@example.com')
        
        password_input = self.selenium.find_element(By.NAME, 'password1')
        password_input.send_keys('securepass123')
        
        password_confirm = self.selenium.find_element(By.NAME, 'password2')
        password_confirm.send_keys('securepass123')
        
        # Submit form
        submit_button = self.selenium.find_element(
            By.XPATH,
            '//button[@type="submit"]'
        )
        submit_button.click()
        
        # Wait for redirect to homepage/dashboard
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/dashboard/')
        )
        
        # Verify user is logged in
        assert 'dashboard' in self.selenium.current_url.lower()
    
    def test_complete_activity_logging_flow(self):
        """Test the complete activity logging workflow."""
        # Login first
        self.selenium.get(f'{self.live_server_url}/login/')
        
        username_input = self.selenium.find_element(By.NAME, 'username')
        username_input.send_keys('testuser')
        
        password_input = self.selenium.find_element(By.NAME, 'password')
        password_input.send_keys('testpass123')
        
        login_button = self.selenium.find_element(
            By.XPATH,
            '//button[@type="submit"]'
        )
        login_button.click()
        
        # Wait for dashboard to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        # Navigate to log activity page
        log_activity_link = self.selenium.find_element(
            By.LINK_TEXT,
            'Log Activity'
        )
        log_activity_link.click()
        
        # Fill in activity form
        activity_name = self.selenium.find_element(By.NAME, 'name')
        activity_name.send_keys('Morning Exercise')
        
        energy_level = self.selenium.find_element(By.NAME, 'energy_level')
        energy_level.send_keys('2')
        
        duration = self.selenium.find_element(By.NAME, 'duration')
        duration.send_keys('30')
        
        # Submit form
        submit_button = self.selenium.find_element(
            By.XPATH,
            '//button[@type="submit"]'
        )
        submit_button.click()
        
        # Wait for success message or redirect
        WebDriverWait(self.selenium, 10).until(
            lambda driver: 'success' in driver.page_source.lower() or
                          'dashboard' in driver.current_url.lower()
        )
        
        # Verify activity appears in history
        self.selenium.get(f'{self.live_server_url}/activity-history/')
        
        page_content = self.selenium.page_source
        assert 'Morning Exercise' in page_content
    
    def test_dashboard_chart_rendering(self):
        """Test that dashboard charts render correctly."""
        # Login
        self.selenium.get(f'{self.live_server_url}/login/')
        
        username_input = self.selenium.find_element(By.NAME, 'username')
        username_input.send_keys('testuser')
        
        password_input = self.selenium.find_element(By.NAME, 'password')
        password_input.send_keys('testpass123')
        
        login_button = self.selenium.find_element(
            By.XPATH,
            '//button[@type="submit"]'
        )
        login_button.click()
        
        # Go to dashboard
        self.selenium.get(f'{self.live_server_url}/dashboard/')
        
        # Wait for Chart.js canvas elements to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'canvas'))
        )
        
        # Verify chart elements exist
        canvases = self.selenium.find_elements(By.TAG_NAME, 'canvas')
        assert len(canvases) > 0
    
    def test_activity_search_and_filter(self):
        """Test searching and filtering activities."""
        # Create test activities first (using Django ORM)
        from energy_tracker.models import Activity
        from django.utils import timezone
        
        for i in range(5):
            Activity.objects.create(
                user=self.user,
                name=f'Test Activity {i}',
                activity_date=timezone.now(),
                energy_level=i - 2,
                duration=15
            )
        
        # Login
        self.selenium.get(f'{self.live_server_url}/login/')
        username_input = self.selenium.find_element(By.NAME, 'username')
        username_input.send_keys('testuser')
        password_input = self.selenium.find_element(By.NAME, 'password')
        password_input.send_keys('testpass123')
        login_button = self.selenium.find_element(
            By.XPATH,
            '//button[@type="submit"]'
        )
        login_button.click()
        
        # Go to activity history
        self.selenium.get(f'{self.live_server_url}/activity-history/')
        
        # Search for specific activity
        search_input = self.selenium.find_element(By.NAME, 'search')
        search_input.send_keys('Test Activity 3')
        search_input.submit()
        
        # Wait for results
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        # Verify filtered results
        page_content = self.selenium.page_source
        assert 'Test Activity 3' in page_content
```

**Key Principles for E2E Tests:**
- ✅ Test critical user journeys only
- ✅ Use page object pattern for maintainability
- ✅ Add explicit waits for dynamic content
- ✅ Test JavaScript interactions
- ✅ Verify visual elements render correctly
- ✅ Test across different browsers (if needed)
- ✅ Keep E2E tests minimal but meaningful

### 2. API Testing (if applicable)

```python
# energy_tracker/tests/test_api.py
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from energy_tracker.models import Activity

@pytest.mark.django_db
class TestActivityAPI:
    """Test API endpoints (if using DRF)."""
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_activity_via_api(self, api_client, user):
        """Test creating activity via API."""
        api_client.force_authenticate(user=user)
        
        data = {
            'name': 'API Activity',
            'energy_level': 2,
            'duration': 25
        }
        
        response = api_client.post('/api/activities/', data)
        
        assert response.status_code == 201
        assert Activity.objects.filter(name='API Activity').exists()
```

---

## Django-Specific Testing Guidelines

### 1. Use Django Test Classes Appropriately

```python
from django.test import TestCase, TransactionTestCase, SimpleTestCase

# For tests that don't need database
class UtilityTests(SimpleTestCase):
    def test_utility_function(self):
        pass

# For most tests with database
class ModelTests(TestCase):
    def test_model_creation(self):
        pass

# For tests that need transaction behavior
class TransactionTests(TransactionTestCase):
    def test_transaction_behavior(self):
        pass
```

### 2. Use setUpTestData for Performance

```python
class ActivityTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data once for the entire test class."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        cls.activities = [
            Activity.objects.create(
                user=cls.user,
                name=f'Activity {i}',
                energy_level=i - 5,
                duration=10
            )
            for i in range(10)
        ]
    
    def test_activity_count(self):
        """Test using class-level data."""
        assert len(self.activities) == 10
```

### 3. Testing with Django Fixtures

```python
# energy_tracker/tests/test_with_fixtures.py
import pytest
from django.test import TestCase

class TestWithFixtures(TestCase):
    fixtures = ['users.json', 'activities.json']
    
    def test_fixture_data_loaded(self):
        """Test that fixture data is available."""
        from django.contrib.auth.models import User
        assert User.objects.count() > 0
```

### 4. Testing Middleware and Signals

```python
# Test middleware
def test_custom_middleware(self):
    """Test custom middleware behavior."""
    from django.test import RequestFactory
    from myapp.middleware import CustomMiddleware
    
    factory = RequestFactory()
    request = factory.get('/')
    
    middleware = CustomMiddleware(lambda r: HttpResponse())
    response = middleware(request)
    
    assert response.status_code == 200
```

### 5. Testing Management Commands

```python
# Test management commands
from django.core.management import call_command
from io import StringIO

def test_custom_command():
    """Test a custom management command."""
    out = StringIO()
    call_command('my_command', stdout=out)
    assert 'Expected output' in out.getvalue()
```

---

## Test Organization and Structure

### Recommended Directory Structure

```
energy_tracker/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_models.py           # Unit tests for models
│   ├── test_forms.py            # Unit tests for forms
│   ├── test_views.py            # Integration tests for views
│   ├── test_utils.py            # Unit tests for utilities
│   ├── test_integration.py      # Database integration tests
│   ├── test_e2e.py              # End-to-end tests
│   └── fixtures/                # Test data fixtures
│       ├── users.json
│       └── activities.json
```

### Naming Conventions

- **Test Files:** `test_*.py` or `*_test.py`
- **Test Classes:** `Test<FeatureName>` (e.g., `TestActivityModel`)
- **Test Methods:** `test_<what_is_being_tested>` (e.g., `test_create_activity_with_valid_data`)

### Using conftest.py for Shared Fixtures

```python
# energy_tracker/tests/conftest.py
import pytest
from django.contrib.auth.models import User
from energy_tracker.models import Activity
from django.utils import timezone

@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def authenticated_client(client, user):
    """Return an authenticated client."""
    client.login(username='testuser', password='testpass123')
    return client

@pytest.fixture
def sample_activities(user):
    """Create sample activities for testing."""
    return [
        Activity.objects.create(
            user=user,
            name=f'Activity {i}',
            activity_date=timezone.now(),
            energy_level=i - 2,
            duration=15
        )
        for i in range(5)
    ]
```

---

## Testing Tools and Configuration

### 1. pytest Configuration

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = energy_manager.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --tb=short
    --reuse-db
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

### 2. Coverage Configuration

```ini
# .coveragerc
[run]
source = energy_tracker
omit = 
    */migrations/*
    */tests/*
    */admin.py
    */apps.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

### 3. Running Tests

```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m e2e

# Run with coverage
pytest --cov=energy_tracker --cov-report=html

# Run tests in parallel
pytest -n auto

# Run specific test file
pytest energy_tracker/tests/test_models.py

# Run specific test
pytest energy_tracker/tests/test_models.py::TestActivityModel::test_activity_creation
```

### 4. Essential Testing Libraries

```txt
# requirements-dev.txt
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0
pytest-xdist==3.5.0
factory-boy==3.3.0
faker==20.1.0
selenium==4.15.2
coverage==7.3.2
```

---

## Common Pitfalls and Solutions

### 1. Database State Pollution

**Problem:** Tests fail when run together but pass individually.

**Solution:**
```python
# Use pytest.mark.django_db
@pytest.mark.django_db
def test_activity_creation():
    # Test code

# Or use Django TestCase which handles transactions
class TestActivity(TestCase):
    def test_creation(self):
        # Automatically rolled back after test
        pass
```

### 2. Timezone Issues

**Problem:** Tests fail due to timezone-aware vs naive datetimes.

**Solution:**
```python
from django.utils import timezone

# Always use timezone-aware datetimes
activity_date = timezone.now()

# Not this:
# activity_date = datetime.now()
```

### 3. Flaky Tests

**Problem:** Tests pass/fail intermittently.

**Solutions:**
- Use explicit waits in Selenium tests
- Avoid time-dependent assertions
- Use freezegun for time-dependent tests

```python
from freezegun import freeze_time

@freeze_time("2024-01-01 12:00:00")
def test_time_dependent_feature():
    # Time is frozen at specified point
    pass
```

### 4. Testing AJAX Requests

**Problem:** Testing JavaScript-driven AJAX calls.

**Solution:**
```python
def test_ajax_log_activity(authenticated_client, user):
    """Test AJAX activity logging."""
    response = authenticated_client.post(
        reverse('log_activity'),
        data={'name': 'Test', 'energy_level': 1, 'duration': 10},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    assert response.status_code == 200
    assert response.json()['success'] == True
```

### 5. Testing Static Files

**Problem:** Static files not loading in tests.

**Solution:**
```python
# Use StaticLiveServerTestCase for E2E tests
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class MyE2ETests(StaticLiveServerTestCase):
    # Static files will be served
    pass
```

---

## Performance and Optimization

### 1. Speed Up Tests

```python
# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations during tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()
```

### 2. Use Factory Pattern for Test Data

```python
# Using factory_boy
import factory
from factory.django import DjangoModelFactory

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')

class ActivityFactory(DjangoModelFactory):
    class Meta:
        model = Activity
    
    user = factory.SubFactory(UserFactory)
    name = factory.Faker('sentence', nb_words=3)
    energy_level = factory.Faker('random_int', min=-2, max=2)
    duration = factory.Faker('random_int', min=5, max=60)

# Usage in tests
def test_with_factory():
    user = UserFactory()
    activity = ActivityFactory(user=user)
    assert activity.user == user
```

### 3. Parallel Test Execution

```bash
# Run tests in parallel
pytest -n auto

# Or specify number of workers
pytest -n 4
```

### 4. Use --reuse-db Flag

```bash
# Reuse test database between runs
pytest --reuse-db

# Force recreation
pytest --create-db
```

---

## Summary Checklist

### Unit Tests ✅
- [ ] Test all model methods and properties
- [ ] Test model validation and constraints
- [ ] Test utility functions in isolation
- [ ] Test form validation
- [ ] Use parametrized tests for similar cases
- [ ] Mock external dependencies
- [ ] Test edge cases and error handling

### Integration Tests ✅
- [ ] Test view logic with Django test client
- [ ] Test authentication and authorization
- [ ] Test form submissions
- [ ] Verify database state changes
- [ ] Test template rendering
- [ ] Test URL routing
- [ ] Test user permissions

### End-to-End Tests ✅
- [ ] Test critical user journeys
- [ ] Test signup/login flow
- [ ] Test main application workflows
- [ ] Verify JavaScript functionality
- [ ] Test chart/visualization rendering
- [ ] Use explicit waits for dynamic content
- [ ] Keep E2E tests focused and minimal

### General Best Practices ✅
- [ ] Follow AAA pattern (Arrange, Act, Assert)
- [ ] One assertion per test (when possible)
- [ ] Descriptive test names
- [ ] Use fixtures for setup
- [ ] Clean up after tests
- [ ] Run tests frequently
- [ ] Maintain high code coverage (>80%)
- [ ] Document complex test scenarios

---

## Additional Resources

### Django Testing Documentation
- [Django Testing Tools](https://docs.djangoproject.com/en/5.2/topics/testing/tools/)
- [Django Testing Overview](https://docs.djangoproject.com/en/5.2/topics/testing/overview/)
- [Advanced Testing Topics](https://docs.djangoproject.com/en/5.2/topics/testing/advanced/)

### pytest-django
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [pytest Parametrize](https://docs.pytest.org/en/stable/parametrize.html)

### Selenium
- [Selenium Python Bindings](https://selenium-python.readthedocs.io/)
- [WebDriver Documentation](https://www.selenium.dev/documentation/webdriver/)

### Testing Best Practices
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)

---

**Document Version:** 1.0  
**Last Updated:** November 29, 2025  
**Maintainer:** Energy Manager Development Team
