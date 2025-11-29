"""
Integration tests for authentication and user management views.

Tests cover signup, login, logout, account, and password change functionality.
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from energy_tracker.models import UserProfile


@pytest.mark.integration
@pytest.mark.django_db
class TestSignupView:
    """Tests for user signup functionality."""

    def test_signup_page_accessible(self, client):
        """Test that signup page loads correctly."""
        response = client.get(reverse('signup'))
        assert response.status_code == 200
        assert any('signup.html' in t.name for t in response.templates)

    def test_signup_redirects_authenticated_user(self, authenticated_client):
        """Test that logged-in users are redirected from signup."""
        response = authenticated_client.get(reverse('signup'))
        assert response.status_code == 302
        assert response.url == reverse('homepage')

    def test_successful_signup(self, client):
        """Test successful user registration."""
        signup_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = client.post(reverse('signup'), data=signup_data)
        
        # Check user was created
        assert User.objects.filter(username='newuser').exists()
        user = User.objects.get(username='newuser')
        assert user.email == 'newuser@example.com'
        
        # Check UserProfile was created via signal
        assert UserProfile.objects.filter(user=user).exists()
        
        # Check user is logged in
        assert '_auth_user_id' in client.session
        
        # Check redirect
        assert response.status_code == 302
        assert response.url == reverse('homepage')

    def test_signup_with_invalid_data(self, client):
        """Test signup with mismatched passwords."""
        signup_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!',
        }
        response = client.post(reverse('signup'), data=signup_data)
        
        # No user should be created
        assert not User.objects.filter(username='newuser').exists()
        
        # Form should have errors
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_signup_duplicate_username(self, client, user):
        """Test signup with existing username."""
        signup_data = {
            'username': 'testuser',  # Already exists from fixture
            'email': 'different@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = client.post(reverse('signup'), data=signup_data)
        
        # Should still only be one user with this username
        assert User.objects.filter(username='testuser').count() == 1
        
        # Form should have errors
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors


@pytest.mark.integration
@pytest.mark.django_db
class TestLoginView:
    """Tests for user login functionality."""

    def test_login_page_accessible(self, client):
        """Test that login page loads correctly."""
        response = client.get(reverse('login'))
        assert response.status_code == 200
        assert any('login.html' in t.name for t in response.templates)

    def test_login_redirects_authenticated(self, authenticated_client):
        """Test that logged-in users are redirected from login."""
        response = authenticated_client.get(reverse('login'))
        assert response.status_code == 302
        assert response.url == reverse('homepage')

    def test_successful_login(self, client, user):
        """Test successful login with valid credentials."""
        login_data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = client.post(reverse('login'), data=login_data)
        
        # Check user is logged in
        assert '_auth_user_id' in client.session
        assert int(client.session['_auth_user_id']) == user.id
        
        # Check redirect
        assert response.status_code == 302
        assert response.url == reverse('homepage')

    def test_login_invalid_credentials(self, client, user):
        """Test login with wrong password."""
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = client.post(reverse('login'), data=login_data)
        
        # User should not be logged in
        assert '_auth_user_id' not in client.session
        
        # Should show error
        assert response.status_code == 200

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent username."""
        login_data = {
            'username': 'nonexistent',
            'password': 'somepassword',
        }
        response = client.post(reverse('login'), data=login_data)
        
        # User should not be logged in
        assert '_auth_user_id' not in client.session
        
        # Should show error
        assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.django_db
class TestLogoutView:
    """Tests for user logout functionality."""

    def test_logout_clears_session(self, authenticated_client, user):
        """Test that logout clears the user session."""
        # Verify user is logged in
        assert '_auth_user_id' in authenticated_client.session
        
        # Logout
        response = authenticated_client.get(reverse('logout'))
        
        # Check user is logged out
        assert '_auth_user_id' not in authenticated_client.session
        
        # Check redirect to login
        assert response.status_code == 302
        assert response.url == reverse('login')

    def test_logout_unauthenticated(self, client):
        """Test logout when not authenticated."""
        response = client.get(reverse('logout'))
        
        # Should redirect to login
        assert response.status_code == 302


@pytest.mark.integration
@pytest.mark.django_db
class TestAccountView:
    """Tests for user account view."""

    def test_account_requires_login(self, client):
        """Test that account page requires authentication."""
        response = client.get(reverse('account'))
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_account_shows_user_info(self, authenticated_client, user, profile):
        """Test that account page displays user information."""
        response = authenticated_client.get(reverse('account'))
        
        assert response.status_code == 200
        assert any('account.html' in t.name for t in response.templates)
        
        # Check context contains user info
        assert response.context['user'] == user
        assert 'profile' in response.context or hasattr(user, 'profile')


@pytest.mark.integration
@pytest.mark.django_db
class TestChangePasswordView:
    """Tests for password change functionality."""

    def test_change_password_flow(self, authenticated_client, user):
        """Test successful password change."""
        password_data = {
            'old_password': 'testpass123',
            'new_password1': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!',
        }
        response = authenticated_client.post(
            reverse('change_password'), 
            data=password_data
        )
        
        # Refresh user from database
        user.refresh_from_db()
        
        # Check password was changed
        assert user.check_password('NewSecurePass123!')
        
        # Check user is still logged in
        assert '_auth_user_id' in authenticated_client.session
        
        # Check for success redirect or message
        assert response.status_code in [200, 302]
