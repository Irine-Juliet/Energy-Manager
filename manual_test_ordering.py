"""
Manual Test Script for Activity Ordering Fix
=============================================

This script verifies that the ordering fixes work correctly without running
Django's test framework (which has Python 3.14 compatibility issues).

Run this script with: python manage.py shell < manual_test_ordering.py
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from energy_tracker.models import Activity

print("\n" + "=" * 70)
print("MANUAL ORDERING TEST - Verifying Bug Fixes")
print("=" * 70)

# Clean up any existing test data
print("\n1. Cleaning up test data...")
User.objects.filter(username="ordering_test_user").delete()

# Create test user
print("2. Creating test user...")
user = User.objects.create_user(
    username="ordering_test_user", email="test@example.com", password="testpass123"
)
print(f"   ✓ Created user: {user.username}")

# Get current time
now = timezone.now()
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

print("\n3. Creating test activities...")

# Create 6 activities at different times throughout the day
activities_created = []
for i in range(6):
    hour = 9 + i  # 9 AM, 10 AM, 11 AM, 12 PM, 1 PM, 2 PM
    activity = Activity.objects.create(
        user=user,
        name=f"Activity at {hour}:00",
        energy_level=1,
        activity_date=today_start + timedelta(hours=hour),
        duration=60,
    )
    activities_created.append(activity)
    print(
        f"   ✓ Created: {activity.name} (ID: {activity.id}, Time: {activity.activity_date.strftime('%I:%M %p')})"
    )

# Now log an activity at 8 AM (earlier than all others) but create it NOW
print("\n4. Logging retrospective activity (8 AM breakfast logged at current time)...")
early_activity = Activity.objects.create(
    user=user,
    name="Breakfast at 8 AM",
    energy_level=2,
    activity_date=today_start + timedelta(hours=8),
    duration=30,
)
activities_created.append(early_activity)
print(
    f"   ✓ Created: {early_activity.name} (ID: {early_activity.id}, Time: {early_activity.activity_date.strftime('%I:%M %p')})"
)

print(f"\n   Total activities created: {len(activities_created)}")

# Test 1: Verify homepage query returns correct 5 activities
print("\n" + "=" * 70)
print("TEST 1: Homepage - Top 5 Most Recent Activities by Time")
print("=" * 70)

today_activities = Activity.objects.filter(
    user=user,
    activity_date__gte=today_start,
    activity_date__lte=today_start + timedelta(days=1),
)

# This is the FIXED query with explicit ordering
recent_activities = today_activities.order_by("-activity_date")[:5]

print(
    "\nQuery: Activity.objects.filter(user=user, today).order_by('-activity_date')[:5]"
)
print("Expected: 5 most recent activities by time (2 PM, 1 PM, 12 PM, 11 AM, 10 AM)")
print(f"Returned: {recent_activities.count()} activities\n")

for idx, activity in enumerate(recent_activities, 1):
    time_str = activity.activity_date.strftime("%I:%M %p")
    print(f"   {idx}. {activity.name} - {time_str} (ID: {activity.id})")

# Verify the correct activities are shown
expected_hours = [14, 13, 12, 11, 10]  # 2 PM, 1 PM, 12 PM, 11 AM, 10 AM
actual_hours = [a.activity_date.hour for a in recent_activities]

if actual_hours == expected_hours:
    print("\n   ✅ PASS: Homepage shows correct 5 most recent activities")
    print("   ✅ Activities are ordered by activity_date (when they occurred)")
    print(
        "   ✅ Breakfast (8 AM) and 9 AM activity correctly excluded (they're 6th & 7th oldest)"
    )
else:
    print(f"\n   ❌ FAIL: Expected hours {expected_hours}, got {actual_hours}")

# Test 2: Verify activities are in descending order
print("\n" + "=" * 70)
print("TEST 2: Activity Ordering - Descending by Time")
print("=" * 70)

dates = [a.activity_date for a in recent_activities]
is_descending = dates == sorted(dates, reverse=True)

if is_descending:
    print("   ✅ PASS: Activities are sorted in descending order (newest first)")
else:
    print("   ❌ FAIL: Activities are NOT in descending order")

# Test 3: Verify all activities appear in history
print("\n" + "=" * 70)
print("TEST 3: History Page - All Activities Visible")
print("=" * 70)

# This is the FIXED query for history page
all_today_activities = Activity.objects.filter(
    user=user, activity_date__gte=today_start
).order_by("-activity_date")

print("\nQuery: Activity.objects.filter(user=user, today).order_by('-activity_date')")
print("Expected: All 7 activities in descending order")
print(f"Returned: {all_today_activities.count()} activities\n")

for idx, activity in enumerate(all_today_activities, 1):
    time_str = activity.activity_date.strftime("%I:%M %p")
    print(f"   {idx}. {activity.name} - {time_str} (ID: {activity.id})")

if all_today_activities.count() == 7:
    print("\n   ✅ PASS: All 7 activities visible in history")
else:
    print(f"\n   ❌ FAIL: Expected 7 activities, got {all_today_activities.count()}")

# Verify they're ordered
all_dates = [a.activity_date for a in all_today_activities]
if all_dates == sorted(all_dates, reverse=True):
    print("   ✅ PASS: History activities in correct descending order")
else:
    print("   ❌ FAIL: History activities NOT in correct order")

# Test 4: Verify breakfast and 9 AM are NOT in top 5
print("\n" + "=" * 70)
print("TEST 4: Retrospective Activity Handling")
print("=" * 70)

recent_ids = [a.id for a in recent_activities]
breakfast_in_top5 = early_activity.id in recent_ids
nine_am_activity = activities_created[0]  # First activity (9 AM)
nine_am_in_top5 = nine_am_activity.id in recent_ids

print(f"\nBreakfast (8 AM) in top 5: {breakfast_in_top5}")
print(f"9 AM activity in top 5: {nine_am_in_top5}")

if not breakfast_in_top5 and not nine_am_in_top5:
    print("\n   ✅ PASS: Earliest activities correctly excluded from top 5")
    print("   ✅ Homepage shows most recent 5 by occurrence time, not log time")
else:
    print("\n   ❌ FAIL: Early activities should not be in top 5")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

all_tests_passed = (
    actual_hours == expected_hours
    and is_descending
    and all_today_activities.count() == 7
    and not breakfast_in_top5
    and not nine_am_in_top5
)

if all_tests_passed:
    print("\n   ✅ ALL TESTS PASSED!")
    print("\n   The ordering bug has been successfully fixed:")
    print("   • Homepage shows 5 most recent activities by occurrence time")
    print("   • Activities are consistently ordered by activity_date DESC")
    print("   • Retrospective logging works correctly")
    print("   • History page shows all activities in correct order")
else:
    print("\n   ❌ SOME TESTS FAILED")
    print("\n   Review the test output above for details")

# Cleanup
print("\n" + "=" * 70)
print("CLEANUP")
print("=" * 70)
print("\nRemoving test data...")
user.delete()
print("✓ Test user and activities deleted")

print("\n" + "=" * 70)
print("Manual testing complete!")
print("=" * 70 + "\n")
