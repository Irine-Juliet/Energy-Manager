"""
Shared pytest fixtures for energy_tracker tests.

This module provides reusable fixtures for testing the Energy Manager application.
"""

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.utils import timezone
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from energy_tracker.models import Activity, UserProfile
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def another_user(db):
    """Create a second test user for isolation tests."""
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='pass123'
    )


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(client, user):
    """Client logged in as testuser."""
    client.login(username='testuser', password='testpass123')
    return client


@pytest.fixture
def activity(user):
    """Create a single test activity."""
    return Activity.objects.create(
        user=user,
        name='Test Activity',
        energy_level=2,
        duration=60,
        activity_date=timezone.now()
    )


@pytest.fixture
def activities_today(user):
    """Create 5 activities for today."""
    now = timezone.now()
    activities = []
    for i in range(5):
        activities.append(Activity.objects.create(
            user=user,
            name=f'Activity {i}',
            energy_level=(-2 if i == 0 else -1 if i == 1 else 1 if i == 3 else 2),
            duration=30 + (i * 10),
            activity_date=now - timedelta(hours=i)
        ))
    return activities


@pytest.fixture
def profile(user):
    """Get or create user profile."""
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


# E2E Test Fixtures

@pytest.fixture(scope='function')
def chrome_options():
    """Configure Chrome options for headless testing."""
    options = ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    return options


@pytest.fixture(scope='function')
def browser(chrome_options):
    """Create a Chrome WebDriver instance for E2E tests."""
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.fixture(scope='function')
def live_server_url(live_server):
    """Provide the live server URL for E2E tests."""
    return live_server.url


@pytest.fixture
def e2e_user(db):
    """Create a user specifically for E2E tests."""
    return User.objects.create_user(
        username='e2euser',
        email='e2e@example.com',
        password='e2epass123'
    )
