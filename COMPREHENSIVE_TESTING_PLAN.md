# Comprehensive Testing Plan for Energy Manager Application

**Date:** November 29, 2025  
**Project:** Energy Manager - Personal Energy Tracking Application  
**Framework:** Django 5.0 with pytest-django  
**Current Status:** Partial test coverage with existing tests

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current Test Inventory](#current-test-inventory)
3. [Testing Strategy Overview](#testing-strategy-overview)
4. [Phase 1: Unit Tests](#phase-1-unit-tests)
5. [Phase 2: Integration Tests](#phase-2-integration-tests)
6. [Phase 3: End-to-End Tests](#phase-3-end-to-end-tests)
7. [Phase 4: Performance & Security Tests](#phase-4-performance--security-tests)
8. [Test Organization & Infrastructure](#test-organization--infrastructure)
9. [Implementation Timeline](#implementation-timeline)
10. [Quality Gates & Acceptance Criteria](#quality-gates--acceptance-criteria)
11. [Maintenance & Continuous Improvement](#maintenance--continuous-improvement)

---

## Executive Summary

### Purpose
This plan provides a systematic approach to create comprehensive test coverage for the Energy Manager application, updating existing tests and adding new ones following industry best practices.

### Goals
- Achieve **80%+ code coverage** across all modules
- Implement comprehensive **unit, integration, and E2E tests**
- **Rewrite/update existing tests** to follow pytest best practices
- Establish **automated test infrastructure** with CI/CD integration
- Ensure **maintainable, readable test code**

### Key Metrics
- **Current Coverage:** ~25% (estimated based on existing tests)
- **Target Coverage:** 80%+ overall, 90%+ for critical paths
- **Test Count Target:** 150+ tests across all levels
- **Execution Time Target:** <2 minutes for full suite

---

## Current Test Inventory

### Existing Test Files

#### 1. `energy_tracker/tests.py`
**Current State:** Basic integration tests using Django TestCase  
**Tests Count:** 13 tests  
**Coverage Areas:**
- Activity form validation (future date rejection)
- Log activity view (POST creates activity)
- Dashboard hour counting (duration aggregation)
- Edge cases (no activities, very short/long durations, today-only filtering)

**Issues to Address:**
- Mixed use of Django TestCase and pytest patterns
- No fixtures for reusable test data
- Limited assertion variety
- Missing negative test cases
- No parameterized tests

**Action Required:** ✅ **REWRITE** - Convert to pytest with fixtures and better organization

#### 2. `energy_tracker/tests_ordering.py`
**Current State:** Comprehensive ordering tests using Django TestCase  
**Tests Count:** 10 tests  
**Coverage Areas:**
- Homepage recent activities ordering
- History page chronological ordering
- Dashboard ordering
- Retrospective logging scenarios
- Same-hour activity ordering
- Empty state handling
- Filtering with ordering

**Issues to Address:**
- Uses Django TestCase instead of pytest
- Could benefit from fixtures
- Some tests are quite long (could be split)
- Limited use of parametrization

**Action Required:** ✅ **UPDATE** - Convert to pytest and optimize with fixtures

### Coverage Gaps

**Critical Missing Tests:**
1. **Model Layer:**
   - Activity model methods (`get_duration_display()`, `get_energy_emoji()`)
   - UserProfile model and signal handlers
   - Model validation edge cases
   - Database constraints and indexes

2. **View Layer:**
   - Signup view with various edge cases
   - Login/logout flows
   - Account management views
   - Settings view
   - Autocomplete API endpoint
   - Bulk delete functionality
   - Error handling (404, 403, 500)

3. **Form Layer:**
   - SignUpForm validation
   - ActivityForm duration calculation edge cases
   - SettingsForm validation

4. **Utility Functions:**
   - `get_canonical_activity_name()` with various scenarios

5. **Authentication & Authorization:**
   - Permission checks across all views
   - Session management
   - Password change flows

6. **API Endpoints:**
   - Autocomplete endpoint edge cases
   - AJAX request handling

7. **Business Logic:**
   - Dashboard analytics calculations
   - Weekly trend aggregation
   - Top draining/energizing activity identification

---

## Testing Strategy Overview

### Testing Pyramid Distribution

```
        /\
       /  \
      /E2E \     ← 10% (~15 tests) - Critical user journeys
     /______\
    /        \
   /Integration\ ← 30% (~45 tests) - View + DB + Form integration
  /____________\
 /              \
/  Unit Tests    \ ← 60% (~90 tests) - Models, Utils, Forms
/________________\
```

### Test Categories by Priority

**P0 (Critical - Must Have):**
- User authentication flows
- Activity CRUD operations
- Dashboard data accuracy
- Activity ordering logic
- Data isolation between users

**P1 (High - Should Have):**
- Form validation
- Error handling
- Edge cases (empty states, boundaries)
- Timezone handling
- Search and filtering

**P2 (Medium - Nice to Have):**
- Performance tests
- Concurrency tests
- Browser compatibility (E2E)
- Accessibility tests

**P3 (Low - Future):**
- Load testing
- Stress testing
- Security penetration testing

---

## Phase 1: Unit Tests

### Overview
**Goal:** Test individual components in isolation  
**Target:** 90 unit tests  
**Coverage Target:** 90%+ for models, forms, utils

---

### Step 1.1: Model Unit Tests

**File:** `energy_tracker/tests/test_models.py`  
**Action:** CREATE NEW  
**Estimated Tests:** 25

#### Test Classes & Methods

##### TestActivityModel (15 tests)

1. **test_activity_creation_with_valid_data**
   - Create activity with all required fields
   - Assert all fields are saved correctly
   - Verify timestamps (created_at, updated_at) are set

2. **test_activity_default_values**
   - Create activity without optional fields
   - Verify default duration (60 minutes)
   - Verify activity_date defaults to timezone.now()

3. **test_energy_level_choices_valid**
   - Parametrize test for all valid energy levels: -2, -1, 1, 2
   - Create activity with each level
   - Assert successful creation

4. **test_energy_level_invalid_zero**
   - Attempt to create activity with energy_level=0 (not in CHOICES)
   - Should fail or be rejected (depending on model validation)

5. **test_energy_level_out_of_range**
   - Test values: -3, 3, 5, -10
   - Should raise ValidationError or similar

6. **test_duration_validation_minimum**
   - Test duration = 1 (valid)
   - Test duration = 0 (invalid)
   - Test duration = -5 (invalid)

7. **test_duration_validation_maximum**
   - Test duration = 1440 (valid, 24 hours)
   - Test duration = 1441 (invalid)
   - Test duration = 10000 (invalid)

8. **test_activity_ordering**
   - Create 5 activities with different activity_dates
   - Query Activity.objects.all()
   - Assert order is by -activity_date (most recent first)

9. **test_str_method**
   - Create activity
   - Assert __str__() contains name
   - Assert format matches expected pattern

10. **test_get_duration_display**
    - Test various durations:
      - 60 → "1h"
      - 90 → "1h 30m"
      - 30 → "30m"
      - 0 → "0m"
      - 125 → "2h 5m"

11. **test_get_energy_emoji**
    - Parametrize for all energy levels
    - Assert correct emoji returned:
      - -2 → '😫'
      - -1 → '😔'
      - 1 → '😊'
      - 2 → '🚀'

12. **test_activity_user_relationship**
    - Create user and activity
    - Assert activity.user == user
    - Assert user.activities.count() == 1

13. **test_cascade_delete_user_activities**
    - Create user with 3 activities
    - Delete user
    - Assert all activities are deleted

14. **test_activity_timestamps**
    - Create activity
    - Assert created_at is set
    - Assert updated_at equals created_at initially
    - Update activity
    - Assert updated_at > created_at

15. **test_activity_description_optional**
    - Create activity without description
    - Assert description is empty string
    - Create activity with description
    - Assert description is saved

##### TestUserProfileModel (10 tests)

16. **test_profile_creation_on_user_signup**
    - Create user
    - Assert UserProfile is auto-created via signal
    - Verify default values (theme=THEME_LIGHT, notifications=True)

17. **test_profile_str_method**
    - Create user and profile
    - Assert str(profile) contains username

18. **test_theme_choices**
    - Test theme='light' is valid
    - Test theme='dark' is valid
    - Test theme='invalid' is rejected

19. **test_notifications_boolean**
    - Test notifications=True
    - Test notifications=False
    - Verify boolean field behavior

20. **test_profile_one_to_one_relationship**
    - Create user
    - Access user.profile
    - Assert profile exists
    - Assert profile.user == user

21. **test_profile_update**
    - Create profile
    - Change theme to 'dark'
    - Save and refresh from db
    - Assert theme is 'dark'

22. **test_profile_cascade_delete**
    - Create user with profile
    - Delete user
    - Assert profile is also deleted

23. **test_profile_signal_on_existing_user**
    - Create user (profile auto-created)
    - Delete profile manually
    - Save user again
    - Assert profile is recreated via signal

24. **test_default_theme_value**
    - Create user
    - Assert profile.theme == UserProfile.THEME_LIGHT

25. **test_default_notifications_value**
    - Create user
    - Assert profile.notifications == True

---

### Step 1.2: Form Unit Tests

**File:** `energy_tracker/tests/test_forms.py`  
**Action:** CREATE NEW (rewrite existing form tests)  
**Estimated Tests:** 30

#### Test Classes & Methods

##### TestActivityForm (20 tests)

1. **test_valid_form_all_fields**
   - Provide all valid fields
   - Assert form.is_valid() == True

2. **test_valid_form_minimum_required**
   - Provide only required fields
   - Assert form is valid

3. **test_name_required**
   - Submit form with empty name
   - Assert form.is_valid() == False
   - Assert 'name' in form.errors

4. **test_name_max_length**
   - Test name with 100 characters (valid)
   - Test name with 101 characters (invalid)

5. **test_name_whitespace_only**
   - Submit form with name=" "
   - Assert form is invalid
   - Verify error message

6. **test_energy_level_required**
   - Submit form without energy_level
   - Assert form is invalid

7. **test_energy_level_valid_choices**
   - Parametrize: [-2, -1, 1, 2]
   - Assert all are valid

8. **test_energy_level_invalid_choices**
   - Parametrize: [0, 3, -3, 'invalid']
   - Assert all are invalid

9. **test_duration_hours_valid**
   - Test hours: 0, 1, 12, 23, 24
   - Assert all valid

10. **test_duration_hours_out_of_range**
    - Test hours: -1, 25, 100
    - Assert invalid

11. **test_duration_minutes_valid**
    - Test minutes: 0, 30, 59
    - Assert all valid

12. **test_duration_minutes_out_of_range**
    - Test minutes: -1, 60, 100
    - Assert invalid

13. **test_duration_calculation_combined**
    - Test hours=2, minutes=30 → duration=150
    - Test hours=0, minutes=15 → duration=15
    - Test hours=1, minutes=0 → duration=60

14. **test_minimum_duration_validation**
    - Test hours=0, minutes=0 → invalid
    - Assert error: "Activity must be at least 1 minute"

15. **test_maximum_duration_validation**
    - Test hours=24, minutes=1 → invalid (1441 minutes)
    - Assert error: "Activity cannot exceed 24 hours"

16. **test_activity_date_in_past**
    - Provide date 1 day ago
    - Assert valid

17. **test_activity_date_current**
    - Provide timezone.now()
    - Assert valid

18. **test_activity_date_future**
    - Provide date 1 day in future
    - Assert invalid
    - Assert error: "Cannot log activities in the future"

19. **test_form_initial_values_on_edit**
    - Create activity with duration=150 (2h 30m)
    - Initialize form with instance=activity
    - Assert initial['duration_hours'] == 2
    - Assert initial['duration_minutes'] == 30

20. **test_form_widgets_and_attributes**
    - Initialize form
    - Assert name widget has correct CSS classes
    - Assert autocomplete='off' for name field
    - Assert energy_level is HiddenInput

##### TestSignUpForm (7 tests)

21. **test_valid_signup_form**
    - Provide username, email, password1, password2
    - Assert form is valid

22. **test_passwords_must_match**
    - password1='pass123', password2='different'
    - Assert invalid
    - Assert error about password mismatch

23. **test_email_required**
    - Submit without email
    - Assert form is invalid

24. **test_email_format_validation**
    - Test valid: 'user@example.com'
    - Test invalid: 'notanemail', 'missing@domain'

25. **test_username_already_exists**
    - Create user with username='testuser'
    - Try to sign up with same username
    - Assert form invalid

26. **test_password_strength_requirements**
    - Test weak password: '123'
    - Assert Django's built-in validators reject it

27. **test_form_widget_classes**
    - Initialize form
    - Assert all fields have correct Tailwind classes

##### TestSettingsForm (3 tests)

28. **test_valid_settings_form**
    - Provide theme='dark', notifications=False
    - Assert valid

29. **test_theme_choices**
    - Test 'light' and 'dark' are valid
    - Test 'invalid_theme' is rejected

30. **test_notifications_boolean**
    - Test True and False
    - Test invalid values rejected

---

### Step 1.3: Utility Function Tests

**File:** `energy_tracker/tests/test_utils.py`  
**Action:** CREATE NEW  
**Estimated Tests:** 10

#### Test Classes & Methods

##### TestGetCanonicalActivityName (10 tests)

1. **test_no_existing_activities_returns_input**
   - Call with name='Meeting' for user with no activities
   - Assert returns 'Meeting' (unchanged)

2. **test_exact_match_returns_input**
   - Create activity with name='Meeting'
   - Call with 'Meeting'
   - Assert returns 'Meeting'

3. **test_case_insensitive_match_single**
   - Create activity 'Meeting'
   - Call with 'meeting' (lowercase)
   - Assert returns 'Meeting' (most common casing)

4. **test_case_insensitive_match_multiple_same_count**
   - Create 1 activity 'Meeting', 1 activity 'meeting'
   - Call with 'MEETING'
   - Assert returns one of them (most recent due to ordering)

5. **test_returns_most_common_casing**
   - Create 5 activities 'Meeting'
   - Create 2 activities 'meeting'
   - Call with 'MEETING'
   - Assert returns 'Meeting' (has count=5)

6. **test_whitespace_trimmed**
   - Call with '  Meeting  '
   - Assert whitespace is stripped in query and return

7. **test_different_users_isolated**
   - User A has activity 'Meeting' (capitalized)
   - User B has activity 'meeting' (lowercase)
   - Call for User B with 'MEETING'
   - Assert returns 'meeting' (User B's version)

8. **test_empty_string_input**
   - Call with ''
   - Assert returns '' or raises error (document expected behavior)

9. **test_special_characters_in_name**
   - Create activity 'Team Meeting #1'
   - Call with 'team meeting #1'
   - Assert returns 'Team Meeting #1'

10. **test_unicode_characters**
    - Create activity 'Café Break'
    - Call with 'café break'
    - Assert case-insensitive matching works with unicode

---

### Step 1.4: Update Existing Form Tests

**File:** `energy_tracker/tests.py` → Move to `energy_tracker/tests/test_forms.py`  
**Action:** REWRITE AND INTEGRATE  

**Existing Test to Update:**
- `test_rejects_future_activity_date` → Already covered in new test #18 above
- **Action:** Remove from old file, ensure new test is more comprehensive

---

## Phase 2: Integration Tests

### Overview
**Goal:** Test components working together (views + models + forms + database)  
**Target:** 45 integration tests  
**Coverage Target:** 85%+ for views

---

### Step 2.1: Authentication & User Management Tests

**File:** `energy_tracker/tests/test_auth_views.py`  
**Action:** CREATE NEW  
**Estimated Tests:** 15

#### Test Classes & Methods

##### TestSignupView (5 tests)

1. **test_signup_page_accessible**
   - GET /signup/
   - Assert status_code=200
   - Assert correct template used

2. **test_signup_redirects_authenticated_user**
   - Login first
   - GET /signup/
   - Assert redirects to homepage

3. **test_successful_signup**
   - POST valid signup data
   - Assert User created
   - Assert UserProfile created via signal
   - Assert user logged in automatically
   - Assert redirects to homepage

4. **test_signup_with_invalid_data**
   - POST invalid data (mismatched passwords)
   - Assert no user created
   - Assert form errors displayed

5. **test_signup_duplicate_username**
   - Create user 'testuser'
   - POST signup with same username
   - Assert error message
   - Assert no second user created

##### TestLoginView (5 tests)

6. **test_login_page_accessible**
   - GET /login/
   - Assert status_code=200

7. **test_login_redirects_authenticated**
   - Login first
   - GET /login/
   - Assert redirects to homepage

8. **test_successful_login**
   - Create user
   - POST valid credentials
   - Assert user logged in
   - Assert session created
   - Assert redirects to homepage

9. **test_login_invalid_credentials**
   - POST wrong password
   - Assert not logged in
   - Assert error message

10. **test_login_nonexistent_user**
    - POST credentials for non-existent user
    - Assert error message

##### TestLogoutView (2 tests)

11. **test_logout_clears_session**
    - Login first
    - GET /logout/
    - Assert user logged out
    - Assert session cleared
    - Assert redirects to login

12. **test_logout_unauthenticated**
    - GET /logout/ without login
    - Assert redirects appropriately

##### TestAccountView (2 tests)

13. **test_account_requires_login**
    - GET /account/ unauthenticated
    - Assert redirects to login

14. **test_account_shows_user_info**
    - Login
    - GET /account/
    - Assert user info in context
    - Assert profile in context

##### TestChangePasswordView (1 test)

15. **test_change_password_flow**
    - Login
    - POST valid password change data
    - Assert password changed
    - Assert user still logged in
    - Assert success message

---

### Step 2.2: Activity CRUD Views Tests

**File:** `energy_tracker/tests/test_activity_views.py`  
**Action:** CREATE NEW (incorporate existing tests from tests.py)  
**Estimated Tests:** 20

#### Test Classes & Methods

##### TestLogActivityView (8 tests)

1. **test_log_activity_requires_authentication**
   - GET /log-activity/ unauthenticated
   - Assert redirect to login

2. **test_log_activity_get_displays_form**
   - Login and GET /log-activity/
   - Assert ActivityForm in context
   - Assert correct template

3. **test_log_activity_post_valid_creates_activity**
   - Login and POST valid activity data
   - Assert Activity created in database
   - Assert activity.user == logged-in user
   - Assert success message
   - Assert redirect

4. **test_log_activity_post_invalid_shows_errors**
   - POST invalid data (empty name)
   - Assert no activity created
   - Assert form errors in response

5. **test_log_activity_normalizes_name_casing**
   - Create existing activity 'Meeting' (5 times)
   - POST new activity 'meeting' (lowercase)
   - Assert saved as 'Meeting' (canonical)

6. **test_log_activity_uses_current_time_if_not_provided**
   - POST without activity_date
   - Assert activity.activity_date is approximately now

7. **test_log_activity_ajax_request**
   - POST with X-Requested-With: XMLHttpRequest header
   - Assert JSON response
   - Assert success=True in JSON

8. **test_log_activity_ajax_invalid**
   - POST invalid data with AJAX
   - Assert JSON response with errors
   - Assert status_code=400

##### TestEditActivityView (5 tests)

9. **test_edit_activity_requires_authentication**
   - GET /activity/1/edit/ unauthenticated
   - Assert redirect to login

10. **test_edit_activity_get_shows_form**
    - Create activity
    - GET edit URL
    - Assert form pre-populated with activity data

11. **test_edit_activity_post_updates**
    - Create activity
    - POST updated data
    - Refresh activity from db
    - Assert changes saved

12. **test_edit_activity_user_isolation**
    - User A creates activity
    - User B tries to edit it
    - Assert 404 or 403

13. **test_edit_nonexistent_activity**
    - GET /activity/99999/edit/
    - Assert 404

##### TestDeleteActivityView (4 tests)

14. **test_delete_activity_requires_authentication**
    - GET delete URL unauthenticated
    - Assert redirect

15. **test_delete_activity_get_confirmation**
    - GET delete URL
    - Assert confirmation page displayed

16. **test_delete_activity_post_deletes**
    - Create activity
    - POST to delete URL
    - Assert activity deleted from db
    - Assert success message

17. **test_delete_activity_user_isolation**
    - User A creates activity
    - User B tries to delete
    - Assert 404 or 403

##### TestBulkDeleteView (3 tests)

18. **test_bulk_delete_multiple_activities**
    - Create 5 activities
    - POST activity_ids=[1,2,3]
    - Assert 3 activities deleted
    - Assert success message

19. **test_bulk_delete_user_isolation**
    - User A creates activities
    - User B tries to bulk delete User A's activities
    - Assert User A's activities not deleted

20. **test_bulk_delete_empty_selection**
    - POST without activity_ids
    - Assert warning message

---

### Step 2.3: Dashboard & Analytics Views Tests

**File:** `energy_tracker/tests/test_dashboard_views.py`  
**Action:** CREATE NEW (incorporate/rewrite existing dashboard tests)  
**Estimated Tests:** 15

#### Test Classes & Methods

##### TestHomepageView (5 tests)

1. **test_homepage_requires_authentication**
   - GET / unauthenticated
   - Assert redirect to login

2. **test_homepage_shows_today_average**
   - Create 3 activities today with energy: 2, 1, -1
   - GET homepage
   - Assert today_avg = 0.67 (rounded)

3. **test_homepage_recent_activities_limit_5**
   - Create 7 activities today
   - GET homepage
   - Assert recent_activities has exactly 5 items

4. **test_homepage_recent_activities_ordered**
   - Create activities at different times
   - Assert ordered by activity_date desc

5. **test_homepage_empty_state**
   - No activities
   - Assert today_avg is None
   - Assert recent_activities is empty

##### TestDashboardView (10 tests)

6. **test_dashboard_requires_authentication**
   - GET /dashboard/ unauthenticated
   - Assert redirect

7. **test_dashboard_today_stats**
   - Create today activities
   - Assert today_count correct
   - Assert today_avg correct

8. **test_dashboard_weekly_data_structure**
   - Create activities over 7 days
   - Assert weekly_data JSON is well-formed
   - Assert contains dates, avg_energy, count

9. **test_dashboard_draining_activities_top_3**
   - Create various draining activities
   - Assert top 3 most draining are returned

10. **test_dashboard_energizing_activities_top_3**
    - Create various energizing activities
    - Assert top 3 most energizing returned

11. **test_dashboard_activity_points_json**
    - Create activities today
    - Assert activity_points JSON correct
    - Assert contains id, name, startTime, energy

12. **test_dashboard_hourly_avg_24_hours**
    - Create activities in hours 9, 10, 14
    - Assert hourly_avg[9] has value
    - Assert hourly_avg[0] is null (no data)

13. **test_dashboard_hours_per_category_calculation**
    - Create activity: energy=2, duration=180 (3 hours)
    - Assert hours_per_category['2'] == 3.0

14. **test_dashboard_hours_per_category_multiple_same_level**
    - Create 3 activities with energy=2, duration=60 each
    - Assert hours_per_category['2'] == 3.0

15. **test_dashboard_hours_per_category_today_only**
    - Create activity yesterday with energy=2
    - Create activity today with energy=2, duration=60
    - Assert hours_per_category['2'] == 1.0 (not yesterday's)

---

### Step 2.4: Activity History & Search Tests

**File:** `energy_tracker/tests/test_activity_history.py`  
**Action:** CREATE NEW (incorporate tests_ordering.py logic)  
**Estimated Tests:** 10

#### Test Classes & Methods

##### TestActivityHistoryView (10 tests)

1. **test_history_requires_authentication**
   - GET /activity-history/ unauthenticated
   - Assert redirect

2. **test_history_default_day_view**
   - Create activities today and yesterday
   - GET /activity-history/
   - Assert only today's activities shown

3. **test_history_week_view**
   - Create activities: today, 3 days ago, 10 days ago
   - GET /activity-history/?view=week
   - Assert shows today and 3 days ago, not 10 days

4. **test_history_month_view**
   - Create activities: today, 15 days ago, 40 days ago
   - GET /activity-history/?view=month
   - Assert shows today and 15 days, not 40 days

5. **test_history_energy_filter**
   - Create mix of energizing and draining
   - GET /activity-history/?energy=2
   - Assert only energy=2 activities shown

6. **test_history_search_by_name**
   - Create activities: 'Meeting', 'Exercise', 'Lunch'
   - GET /activity-history/?q=meet
   - Assert only 'Meeting' shown (case-insensitive)

7. **test_history_pagination**
   - Create 25 activities
   - GET /activity-history/
   - Assert page_obj.paginator.num_pages == 2
   - Assert page 1 has 20 items

8. **test_history_ordering_consistent**
   - Create activities at various times
   - Assert ordered by activity_date desc

9. **test_history_user_isolation**
   - User A creates activities
   - User B logs in and views history
   - Assert only User B's activities shown

10. **test_history_combined_filters**
    - GET /activity-history/?view=week&energy=2&q=meet
    - Assert filters combine correctly

---

### Step 2.5: Settings & Preferences Tests

**File:** `energy_tracker/tests/test_settings_views.py`  
**Action:** CREATE NEW  
**Estimated Tests:** 5

#### Test Classes & Methods

##### TestSettingsView (5 tests)

1. **test_settings_requires_authentication**
   - GET /settings/ unauthenticated
   - Assert redirect

2. **test_settings_get_displays_form**
   - Login and GET /settings/
   - Assert SettingsForm in context
   - Assert pre-populated with user's profile

3. **test_settings_update_theme**
   - POST theme='dark'
   - Assert profile.theme == 'dark'
   - Assert cookie set for theme

4. **test_settings_update_notifications**
   - POST notifications=False
   - Assert profile.notifications == False

5. **test_settings_creates_profile_if_missing**
   - Delete user's profile
   - GET /settings/
   - Assert profile recreated

---

### Step 2.6: Autocomplete API Tests

**File:** `energy_tracker/tests/test_autocomplete_api.py`  
**Action:** CREATE NEW  
**Estimated Tests:** 5

#### Test Classes & Methods

##### TestAutocompleteActivities (5 tests)

1. **test_autocomplete_requires_authentication**
   - GET /autocomplete/ unauthenticated
   - Assert 302 or 403

2. **test_autocomplete_returns_suggestions**
   - Create activities: 'Meeting', 'Meeting with team', 'Lunch'
   - GET /autocomplete/?q=meet
   - Assert suggestions contain 'Meeting' and 'Meeting with team'

3. **test_autocomplete_top_5_limit**
   - Create 10 activities matching 'Activity'
   - GET /autocomplete/?q=activity
   - Assert max 5 suggestions returned

4. **test_autocomplete_frequency_ordering**
   - Create 'Meeting' 5 times, 'Meetup' 2 times
   - GET /autocomplete/?q=meet
   - Assert 'Meeting' appears before 'Meetup'

5. **test_autocomplete_empty_query**
   - GET /autocomplete/?q=
   - Assert suggestions=[]

---

## Phase 3: End-to-End Tests

### Overview
**Goal:** Test complete user journeys in a browser-like environment  
**Target:** 15 E2E tests  
**Coverage Target:** Critical user flows

---

### Step 3.1: Setup E2E Testing Infrastructure

**File:** `energy_tracker/tests/test_e2e.py`  
**Action:** CREATE NEW  
**Prerequisites:**
- Install Selenium: `pip install selenium`
- Install browser drivers (ChromeDriver or GeckoDriver)
- Add to requirements-dev.txt

**Base Class Setup:**
```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
```

---

### Step 3.2: E2E Test Cases

#### Test Classes & Methods

##### TestUserJourneyE2E (15 tests)

1. **test_complete_signup_flow**
   - Navigate to signup page
   - Fill form and submit
   - Assert redirected to homepage
   - Assert welcome message

2. **test_complete_login_logout_flow**
   - Navigate to login
   - Login with valid credentials
   - Assert homepage displayed
   - Click logout
   - Assert redirected to login

3. **test_log_single_activity_flow**
   - Login
   - Navigate to log activity
   - Fill form (name, energy, duration)
   - Submit
   - Assert success message
   - Navigate to history
   - Assert activity appears

4. **test_log_multiple_activities_today**
   - Login
   - Log 3 activities
   - Navigate to homepage
   - Assert 3 activities in recent list

5. **test_edit_activity_flow**
   - Login
   - Create activity
   - Navigate to history
   - Click edit on activity
   - Change name and energy
   - Submit
   - Assert changes reflected

6. **test_delete_activity_flow**
   - Login
   - Create activity
   - Navigate to history
   - Click delete
   - Confirm deletion
   - Assert activity removed from list

7. **test_dashboard_chart_rendering**
   - Login
   - Create activities
   - Navigate to dashboard
   - Wait for Chart.js canvas elements
   - Assert charts rendered

8. **test_activity_search_flow**
   - Login
   - Create activities with various names
   - Navigate to history
   - Enter search term
   - Assert filtered results

9. **test_activity_filter_by_energy**
   - Login
   - Create mix of draining/energizing
   - Navigate to history
   - Select energy filter
   - Assert filtered correctly

10. **test_autocomplete_interaction**
    - Login
    - Create repeated activities
    - Navigate to log activity
    - Type in name field
    - Assert autocomplete suggestions appear
    - Click suggestion
    - Assert name filled

11. **test_settings_theme_change**
    - Login
    - Navigate to settings
    - Change theme to dark
    - Submit
    - Assert page reflects dark theme

12. **test_responsive_mobile_view**
    - Set browser to mobile viewport
    - Login
    - Navigate pages
    - Assert mobile-friendly layout

13. **test_pagination_navigation**
    - Login
    - Create 25 activities
    - Navigate to history
    - Assert pagination controls visible
    - Click page 2
    - Assert next 5 activities shown

14. **test_retrospective_activity_logging**
    - Login
    - Log activity with past date (8 AM)
    - Log activity with current time (2 PM)
    - Navigate to homepage
    - Assert current activity in top 5, past activity may not be

15. **test_bulk_delete_activities**
    - Login
    - Create 5 activities
    - Navigate to history
    - Select 3 activities (checkboxes)
    - Click bulk delete
    - Confirm
    - Assert 3 deleted, 2 remain

---

## Phase 4: Performance & Security Tests

### Overview
**Goal:** Ensure application performs well and is secure  
**Target:** 10 tests  
**Coverage Target:** Key performance bottlenecks and security vulnerabilities

---

### Step 4.1: Performance Tests

**File:** `energy_tracker/tests/test_performance.py`  
**Action:** CREATE NEW  
**Estimated Tests:** 5

#### Test Methods

1. **test_homepage_query_count**
   - Use django-debug-toolbar or assertNumQueries
   - Assert homepage loads with <10 DB queries
   - Use select_related/prefetch_related optimizations

2. **test_dashboard_with_many_activities**
   - Create 1000 activities
   - Time dashboard load
   - Assert loads in <1 second

3. **test_history_pagination_performance**
   - Create 1000 activities
   - Time first page load
   - Assert <500ms

4. **test_autocomplete_response_time**
   - Create 100 unique activities
   - Time autocomplete API call
   - Assert <200ms

5. **test_bulk_delete_performance**
   - Create 100 activities
   - Time bulk delete operation
   - Assert <1 second

---

### Step 4.2: Security Tests

**File:** `energy_tracker/tests/test_security.py`  
**Action:** CREATE NEW  
**Estimated Tests:** 5

#### Test Methods

1. **test_csrf_protection_on_forms**
   - POST to log_activity without CSRF token
   - Assert 403 Forbidden

2. **test_sql_injection_protection**
   - Submit activity name with SQL injection attempt
   - Assert safely escaped/rejected

3. **test_xss_protection**
   - Submit activity name with <script> tag
   - Assert escaped in rendered HTML

4. **test_password_hashing**
   - Create user with password
   - Assert password not stored in plaintext
   - Assert uses strong hashing (PBKDF2/Argon2)

5. **test_unauthorized_api_access**
   - Call autocomplete API without login
   - Assert 302 redirect or 403

---

## Test Organization & Infrastructure

### Directory Structure

```
energy_tracker/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures
│   ├── test_models.py                 # Model unit tests
│   ├── test_forms.py                  # Form unit tests
│   ├── test_utils.py                  # Utility function tests
│   ├── test_auth_views.py             # Authentication view tests
│   ├── test_activity_views.py         # Activity CRUD view tests
│   ├── test_dashboard_views.py        # Dashboard & analytics tests
│   ├── test_activity_history.py       # History & search tests
│   ├── test_settings_views.py         # Settings view tests
│   ├── test_autocomplete_api.py       # Autocomplete API tests
│   ├── test_e2e.py                    # End-to-end tests
│   ├── test_performance.py            # Performance tests
│   ├── test_security.py               # Security tests
│   └── fixtures/
│       ├── users.json                 # Sample user data
│       └── activities.json            # Sample activity data
├── tests.py                           # OLD FILE - TO BE REMOVED
└── tests_ordering.py                  # OLD FILE - TO BE REMOVED
```

---

### Pytest Configuration

**File:** `pytest.ini`  
**Action:** UPDATE

```ini
[pytest]
DJANGO_SETTINGS_MODULE = energy_manager.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --tb=short
    --reuse-db
    --cov=energy_tracker
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests for models, forms, utils
    integration: Integration tests for views and database
    e2e: End-to-end browser tests
    slow: Tests that take >1 second
    security: Security-focused tests
    performance: Performance-focused tests
```

---

### Shared Fixtures

**File:** `energy_tracker/tests/conftest.py`  
**Action:** CREATE NEW

```python
import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.utils import timezone
from energy_tracker.models import Activity, UserProfile
from datetime import timedelta


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
            energy_level=(-2 + i),  # -2, -1, 0, 1, 2
            duration=30 + (i * 10),
            activity_date=now - timedelta(hours=i)
        ))
    return activities


@pytest.fixture
def profile(user):
    """Get or create user profile."""
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile
```

---

### Coverage Configuration

**File:** `.coveragerc`  
**Action:** CREATE NEW

```ini
[run]
source = energy_tracker
omit = 
    */migrations/*
    */tests/*
    */admin.py
    */apps.py
    */__pycache__/*
    */venv/*
    */env/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    def __str__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod

precision = 2
show_missing = True
```

---

### CI/CD Integration

**File:** `.github/workflows/django-tests.yml`  
**Action:** UPDATE

```yaml
name: Django Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        ruff check .
        black --check .
    
    - name: Run unit tests
      run: pytest -m unit --cov --cov-report=xml
    
    - name: Run integration tests
      run: pytest -m integration --cov --cov-append --cov-report=xml
    
    - name: Run E2E tests
      run: pytest -m e2e --cov --cov-append --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

---

## Implementation Timeline

### Week 1: Foundation & Unit Tests
**Days 1-2:**
- ✅ Set up test infrastructure (conftest.py, pytest.ini, .coveragerc)
- ✅ Create test directory structure
- ✅ Implement shared fixtures

**Days 3-5:**
- ✅ Write all model unit tests (25 tests)
- ✅ Write all form unit tests (30 tests)
- ✅ Write utility function tests (10 tests)
- ✅ Target: 65 unit tests, 60%+ coverage

**Days 6-7:**
- ✅ Run tests, fix failures
- ✅ Measure coverage, identify gaps
- ✅ Code review and refactor

---

### Week 2: Integration Tests
**Days 8-10:**
- ✅ Write authentication view tests (15 tests)
- ✅ Write activity CRUD view tests (20 tests)
- ✅ Target: 35 integration tests

**Days 11-13:**
- ✅ Write dashboard view tests (15 tests)
- ✅ Write activity history tests (10 tests)
- ✅ Write settings & API tests (10 tests)
- ✅ Target: +35 tests (70 total integration)

**Days 14:**
- ✅ Integration test review
- ✅ Migrate/remove old test files (tests.py, tests_ordering.py)
- ✅ Coverage check: Target 80%+

---

### Week 3: E2E & Specialized Tests
**Days 15-17:**
- ✅ Set up Selenium
- ✅ Write E2E tests (15 tests)
- ✅ Test across browsers (Chrome, Firefox)

**Days 18-19:**
- ✅ Write performance tests (5 tests)
- ✅ Write security tests (5 tests)

**Days 20-21:**
- ✅ Final test run
- ✅ Fix remaining failures
- ✅ Documentation updates
- ✅ CI/CD pipeline verification

---

## Quality Gates & Acceptance Criteria

### Code Coverage Thresholds
- **Overall:** 80% minimum
- **Models:** 90% minimum
- **Views:** 85% minimum
- **Forms:** 90% minimum
- **Utils:** 95% minimum

### Test Quality Metrics
- **Test Naming:** All tests have descriptive names
- **Test Independence:** Each test can run in isolation
- **Test Speed:** Unit tests <10ms each, integration <100ms each
- **Test Reliability:** 0% flaky tests (must pass consistently)

### Documentation Requirements
- ✅ All test files have module docstrings
- ✅ Complex tests have inline comments
- ✅ Fixtures documented in conftest.py
- ✅ README updated with testing instructions

### Acceptance Criteria for Completion
- [ ] 150+ tests implemented
- [ ] 80%+ code coverage achieved
- [ ] All tests passing in CI/CD
- [ ] Old test files removed
- [ ] Coverage reports generated
- [ ] Testing documentation complete

---

## Maintenance & Continuous Improvement

### Test Maintenance Strategy
1. **Run tests before every commit** (use pre-commit hooks)
2. **Review coverage reports weekly**
3. **Add tests for every bug fix**
4. **Add tests for every new feature**
5. **Refactor tests quarterly** to reduce duplication

### Monitoring Test Health
- **Track test execution time** (alert if >2 minutes)
- **Monitor flaky tests** (rewrite if >5% failure rate)
- **Review coverage trends** (alert if drops below 75%)
- **Dependency updates** (test with new library versions)

### Future Test Enhancements
1. **Add mutation testing** (using mutmut)
2. **Add contract testing** (if API evolves)
3. **Add visual regression testing** (for UI)
4. **Add accessibility testing** (using axe-core)
5. **Add load testing** (using Locust)

---

## Appendix

### A. Running Tests

```bash
# Run all tests
pytest

# Run by category
pytest -m unit
pytest -m integration
pytest -m e2e

# Run specific file
pytest energy_tracker/tests/test_models.py

# Run specific test
pytest energy_tracker/tests/test_models.py::TestActivityModel::test_activity_creation_with_valid_data

# Run with coverage
pytest --cov=energy_tracker --cov-report=html

# Run in parallel
pytest -n auto

# Run with verbose output
pytest -v

# Run only failed tests from last run
pytest --lf

# Run and stop on first failure
pytest -x
```

### B. Dependencies to Add

**requirements-dev.txt:**
```
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0
pytest-xdist==3.5.0
factory-boy==3.3.0
faker==20.1.0
selenium==4.15.2
coverage==7.3.2
freezegun==1.4.0
pytest-mock==3.12.0
```

### C. Test Data Factories

Consider implementing factories for complex test data:

```python
# energy_tracker/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from energy_tracker.models import Activity
from django.utils import timezone

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
    energy_level = factory.Faker('random_element', elements=[-2, -1, 1, 2])
    duration = factory.Faker('random_int', min=15, max=120)
    activity_date = factory.LazyFunction(timezone.now)
```

### D. Quick Reference

**Test Markers:**
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow tests
- `@pytest.mark.django_db` - Tests requiring database

**Common Assertions:**
```python
assert obj.field == expected
assert obj.method() is True
assert obj in collection
assert 'substring' in text
assert len(collection) == 5
```

**Django Test Client:**
```python
response = client.get('/url/')
response = client.post('/url/', data={'key': 'value'})
assert response.status_code == 200
assert 'text' in response.content.decode()
assert response.context['key'] == value
```

---

**End of Testing Plan**

This plan provides a comprehensive, step-by-step approach to creating a robust test suite for the Energy Manager application. Follow each phase systematically, and adjust the timeline as needed based on your team's capacity.
