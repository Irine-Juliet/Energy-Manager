"""
Security Tests for Energy Manager Application

Tests for common security vulnerabilities including CSRF, XSS, SQL injection,
authentication, and authorization issues.
"""

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from energy_tracker.models import Activity


@pytest.mark.security
@pytest.mark.django_db
class TestSecurityMeasures:
    """Test suite for security and vulnerability checks."""

    def test_csrf_protection_on_forms(self, user):
        """
        Test that POST requests without CSRF token are rejected.

        Django's CSRF protection should prevent unauthorized form submissions.
        All POST endpoints should require valid CSRF tokens.
        """
        # Create a client without CSRF enforcement to test the protection
        client = Client(enforce_csrf_checks=True)

        # Login the user first
        client.force_login(user)

        # Try to POST to log_activity without CSRF token
        response = client.post(
            reverse("log_activity"),
            {
                "name": "Test Activity",
                "energy_level": 2,
                "duration_hours": 1,
                "duration_minutes": 0,
            },
        )

        # Should be forbidden due to missing CSRF token
        assert (
            response.status_code == 403
        ), f"Expected 403 Forbidden for request without CSRF, got {response.status_code}"

    def test_sql_injection_protection(self, authenticated_client, user):
        """
        Test that SQL injection attempts are safely escaped.

        Django's ORM should protect against SQL injection by parameterizing queries.
        Malicious input should be treated as literal strings, not SQL code.
        """
        # Common SQL injection attempts
        malicious_inputs = [
            "'; DROP TABLE energy_tracker_activity; --",
            "' OR '1'='1",
            "1' UNION SELECT * FROM django_user--",
            "admin'--",
            "' OR 1=1--",
        ]

        for malicious_input in malicious_inputs:
            # Try to create activity with SQL injection attempt in name
            response = authenticated_client.post(
                reverse("log_activity"),
                {
                    "name": malicious_input,
                    "energy_level": 2,
                    "duration_hours": 1,
                    "duration_minutes": 0,
                    "activity_date": timezone.now().date(),
                },
            )

            # Request should succeed (input treated as literal string)
            assert response.status_code in [
                200,
                302,
            ], f"Failed to handle SQL injection attempt: {malicious_input}"

            # If activity was created, verify it's stored as literal string
            if response.status_code == 302:
                activity = Activity.objects.filter(
                    user=user, name=malicious_input
                ).first()

                # Activity should exist with exact malicious string (safely escaped)
                assert activity is not None
                assert activity.name == malicious_input

                # Clean up for next iteration
                activity.delete()

        # Verify the database still exists and is intact
        user_count = User.objects.count()
        assert (
            user_count > 0
        ), "Database tables should still exist after injection attempts"

    def test_xss_protection(self, authenticated_client, user):
        """
        Test that XSS attempts are properly escaped in HTML output.

        User input containing JavaScript should be escaped when rendered,
        preventing script execution in the browser.
        """
        # XSS attack vectors
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror="alert(1)">',
            "<svg/onload=alert(1)>",
            "javascript:alert(1)",
            '<iframe src="javascript:alert(1)">',
        ]

        for payload in xss_payloads:
            # Create activity with XSS payload in name
            Activity.objects.create(
                user=user,
                name=payload,
                energy_level=1,
                duration=60,
                activity_date=timezone.now(),
            )

            # Get the homepage which displays recent activities
            response = authenticated_client.get(reverse("homepage"))
            assert response.status_code == 200

            # Get response content as string
            content = response.content.decode("utf-8")

            # Verify the dangerous payload is escaped
            # Django's template engine should escape < and > to &lt; and &gt;
            # The payload should appear as escaped HTML entities, not executable code
            if "<script>" in payload.lower():
                # For script tags, verify they are escaped
                assert (
                    "&lt;script&gt;" in content or payload not in content
                ), f"XSS payload with script tag not properly escaped: {payload}"
                # Ensure the literal string <script> doesn't appear in user-generated content area
                # (legitimate script tags from the app itself are OK)
                # We check that if <script appears, it's from CDN or app code, not user input
                if "<script" in content:
                    # Verify the escaped version is also present (meaning user input was escaped)
                    assert (
                        "&lt;script" in content
                    ), "Script tag from user input not escaped"

            # Clean up
            Activity.objects.filter(user=user, name=payload).delete()

    def test_password_hashing(self, db):
        """
        Test that passwords are hashed and not stored in plaintext.

        Django should use strong hashing (PBKDF2/Argon2) to store passwords.
        Raw passwords should never be retrievable from the database.
        """
        # Create a user with a known password
        password = "super_secret_password_123"
        user = User.objects.create_user(
            username="securitytest", email="security@test.com", password=password
        )

        # Verify password is not stored in plaintext
        assert user.password != password, "Password should not be stored in plaintext"

        # Verify password field contains a hash
        # Django password format: <algorithm>$<iterations>$<salt>$<hash>
        assert "$" in user.password, "Password should be in hashed format"

        # Verify it uses a strong algorithm (PBKDF2, Argon2, or bcrypt)
        valid_algorithms = ["pbkdf2_sha256", "argon2", "bcrypt"]
        algorithm = user.password.split("$")[0]
        assert any(
            alg in algorithm for alg in valid_algorithms
        ), f"Password should use strong hashing algorithm, found: {algorithm}"

        # Verify the password can be verified (check_password works)
        assert user.check_password(password), "Password verification should work"
        assert not user.check_password(
            "wrong_password"
        ), "Wrong password should not verify"

        # Verify the hash is different even with same password (due to salt)
        user2 = User.objects.create_user(
            username="securitytest2", email="security2@test.com", password=password
        )
        assert (
            user.password != user2.password
        ), "Same password should produce different hashes (salting)"

    def test_unauthorized_api_access(self, client):
        """
        Test that API endpoints require authentication.

        Unauthenticated users should not be able to access protected endpoints
        like autocomplete API.
        """
        # Try to access autocomplete API without authentication
        response = client.get(reverse("autocomplete_activities"), {"q": "test"})

        # Should redirect to login or return 403 Forbidden
        assert response.status_code in [
            302,
            403,
        ], f"Unauthenticated API access should be blocked, got {response.status_code}"

        # If it's a redirect, should redirect to login page
        if response.status_code == 302:
            assert (
                "login" in response.url
            ), f"Should redirect to login page, got: {response.url}"

    def test_user_data_isolation(self, client, user, another_user):
        """
        Test that users can only access their own data.

        Users should not be able to view, edit, or delete other users' activities.
        """
        # Create an activity for user A
        activity = Activity.objects.create(
            user=user,
            name="User A Activity",
            energy_level=2,
            duration=60,
            activity_date=timezone.now(),
        )

        # Login as user B
        client.force_login(another_user)

        # Try to access user A's activity edit page
        response = client.get(reverse("edit_activity", args=[activity.id]))

        # Should get 404 (not found) rather than showing the activity
        # This prevents information disclosure about other users' data
        assert (
            response.status_code == 404
        ), f"User should not access other user's activity, got {response.status_code}"

        # Try to delete user A's activity
        response = client.post(reverse("delete_activity", args=[activity.id]))

        # Should get 404
        assert (
            response.status_code == 404
        ), f"User should not delete other user's activity, got {response.status_code}"

        # Verify the activity still exists (wasn't deleted)
        assert Activity.objects.filter(
            id=activity.id
        ).exists(), "Activity should not be deleted by unauthorized user"

        # Try to view user B's history and ensure user A's activities don't appear
        response = client.get(reverse("activity_history"))
        assert response.status_code == 200

        # Check the paginated activities (page_obj is used for pagination)
        if "page_obj" in response.context:
            activities = response.context["page_obj"].object_list
        elif "activities" in response.context:
            activities = response.context["activities"]
        else:
            # If neither exists, there are no activities which is also valid
            activities = []

        activity_users = [act.user for act in activities]

        # All activities should belong to user B (another_user), not user A
        assert (
            user not in activity_users
        ), "User A's activities should not appear in User B's history"

    def test_session_security(self, authenticated_client, user):
        """
        Test that sessions are properly secured.

        Sessions should expire after logout and sensitive operations
        should require re-authentication.
        """
        # Verify user is logged in
        response = authenticated_client.get(reverse("homepage"))
        assert response.status_code == 200

        # Logout
        response = authenticated_client.get(reverse("logout"))

        # Try to access protected page after logout
        response = authenticated_client.get(reverse("homepage"))

        # Should redirect to login (session cleared)
        assert response.status_code == 302
        assert "login" in response.url

        # Verify session cookie is cleared or invalidated
        # After logout, subsequent requests should not be authenticated
        response = authenticated_client.get(reverse("log_activity"))
        assert response.status_code == 302  # Redirect to login
