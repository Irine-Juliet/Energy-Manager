# Log Activity & History Bug Investigation Plan

## Bug Description
When a user logs an activity for the same day but at an earlier time (e.g., 2-3 hours before the current time), the activity does not appear on the home page. Instead, it gets pushed into the history page under the week section instead of staying in the day section. This makes the home page appear as if no activity was recorded for that day.

**Expected Behavior:**
- Any activity logged within the current day should show on the home page, regardless of the time it was entered
- The history page should correctly place the activity under the day section

---

## Investigation Plan

### Phase 1: Understand the Data Flow
**Objective:** Map out how activity data flows from form submission to display

1. **Trace the Activity Logging Process**
   - [ ] Review `energy_tracker/views.py` → `log_activity_view()` function
   - [ ] Check how `activity_date` is being saved to the database
   - [ ] Verify if the form is correctly processing date/time inputs
   - [ ] Examine `energy_tracker/forms.py` → `ActivityForm` class
   - [ ] Check the `activity_date` field validation and processing

2. **Examine the Model**
   - [ ] Review `energy_tracker/models.py` → `Activity` model
   - [ ] Verify the `activity_date` field type and default value
   - [ ] Check if there are any timezone-related settings or conversions

3. **Review Timezone Handling**
   - [ ] Check `energy_manager/settings.py` for `TIME_ZONE` and `USE_TZ` settings
   - [ ] Verify if `django.utils.timezone.now()` is being used correctly
   - [ ] Look for any timezone conversion issues between form input and database storage

---

### Phase 2: Analyze Home Page Display Logic
**Objective:** Identify why activities aren't showing on the home page

1. **Review Home Page View**
   - [ ] Examine `energy_tracker/views.py` → `homepage_view()` function
   - [ ] Analyze the query filters for "today's activities"
   - [ ] Check how `today_start` and `today_end` are calculated
   - [ ] Verify if timezone-aware datetime comparisons are correct
   - [ ] Test the query logic with sample data

2. **Check Template Rendering**
   - [ ] Review `templates/energy_tracker/homepage.html`
   - [ ] Verify how `recent_activities` are being displayed
   - [ ] Check if there are any filters or conditions hiding activities

3. **Test Query Boundaries**
   - [ ] Manually test the query with different timestamps
   - [ ] Check if activities at exact boundary times (00:00:00, 23:59:59) work
   - [ ] Verify behavior with activities logged in different time zones

---

### Phase 3: Analyze History Page Display Logic
**Objective:** Identify why activities are incorrectly categorized in the week section

1. **Review History Page View**
   - [ ] Examine `energy_tracker/views.py` → `activity_history_view()` function
   - [ ] Analyze the time window filter logic for 'day', 'week', and 'month' views
   - [ ] Check how `start` datetime is calculated for each view mode
   - [ ] Verify the filter: `activities.filter(activity_date__gte=start)`

2. **Check Template Rendering**
   - [ ] Review `templates/energy_tracker/activity_history.html`
   - [ ] Check if there's any client-side JavaScript grouping activities
   - [ ] Verify how the view parameter affects display

3. **Test View Filters**
   - [ ] Test with activities at different times within the same day
   - [ ] Check if the 'day' view correctly shows all activities from 00:00:00 to 23:59:59
   - [ ] Verify 'week' and 'month' view boundaries

---

### Phase 4: Database Inspection
**Objective:** Verify actual data stored in the database

1. **Direct Database Query**
   - [ ] Run Django shell: `python manage.py shell`
   - [ ] Query activities: `Activity.objects.filter(user=<user>).order_by('-activity_date')`
   - [ ] Print `activity_date` values with timezone info
   - [ ] Compare stored times vs. expected times

2. **Check for Data Inconsistencies**
   - [ ] Verify all activities have timezone-aware datetimes
   - [ ] Check if any activities have dates in the future or distant past
   - [ ] Look for any NULL or malformed `activity_date` values

---

### Phase 5: Reproduce the Bug
**Objective:** Create a reproducible test case

1. **Create Test Scenario**
   - [ ] Log an activity at current time
   - [ ] Log an activity at current date but 2 hours earlier
   - [ ] Log an activity at current date but 3 hours earlier
   - [ ] Check home page display
   - [ ] Check history page under 'day' view
   - [ ] Check history page under 'week' view

2. **Document Findings**
   - [ ] Record which activities appear where
   - [ ] Note the exact timestamps stored in the database
   - [ ] Capture screenshots if needed
   - [ ] Document any error messages or console logs

---

### Phase 6: Identify Root Cause
**Objective:** Pinpoint the exact cause of the bug

**Potential Root Causes to Investigate:**

1. **Timezone Mismatch**
   - Server timezone vs. browser timezone mismatch
   - Naive datetime being compared to timezone-aware datetime
   - Incorrect timezone conversion during form processing

2. **Incorrect Date Range Calculation**
   - `today_start` and `today_end` not covering full 24-hour period
   - Using current time instead of day boundaries
   - Off-by-one errors in date comparisons

3. **Form Processing Issue**
   - Hidden datetime field not correctly combining date and time inputs
   - JavaScript not properly formatting datetime before submission
   - Server-side form cleaning modifying the datetime unexpectedly

4. **Query Filter Problems**
   - Using `__gt` instead of `__gte` or vice versa
   - Incorrect filter chaining
   - ORM query not translating to expected SQL

5. **Default Value Override**
   - `activity_date` defaulting to current time instead of user input
   - Form not properly passing the datetime to the model

---

### Phase 7: Verification Tests
**Objective:** Confirm the diagnosis before implementing a fix

1. **Create Unit Tests**
   - [ ] Write test for logging activity at earlier time same day
   - [ ] Write test for homepage query with various timestamps
   - [ ] Write test for history page day/week/month filters

2. **Manual Testing Checklist**
   - [ ] Log activity for "now"
   - [ ] Log activity for "today at 8:00 AM" (if it's currently PM)
   - [ ] Log activity for "today at 11:00 PM" (if it's currently AM)
   - [ ] Verify each appears on homepage
   - [ ] Verify each appears in history 'day' view
   - [ ] Verify pagination doesn't hide activities

---

### Phase 8: Document Findings
**Objective:** Prepare for bug fix implementation

1. **Create Bug Report**
   - [ ] Summarize the root cause
   - [ ] List all affected components
   - [ ] Document the incorrect behavior vs. expected behavior
   - [ ] Include code snippets showing the issue

2. **Propose Solution**
   - [ ] Outline the fix approach
   - [ ] Identify files that need changes
   - [ ] Consider edge cases
   - [ ] Plan for backward compatibility

---

## Key Files to Investigate

### Backend Files
- `energy_tracker/views.py` - `homepage_view()`, `activity_history_view()`, `log_activity_view()`
- `energy_tracker/forms.py` - `ActivityForm` class
- `energy_tracker/models.py` - `Activity` model
- `energy_manager/settings.py` - Timezone settings

### Frontend Files
- `templates/energy_tracker/homepage.html`
- `templates/energy_tracker/activity_history.html`
- `templates/energy_tracker/log_activity.html` - JavaScript datetime handling

### Database
- Check `energy_tracker_activity` table directly

---

## Tools & Commands

### Django Shell Commands
```python
python manage.py shell

from energy_tracker.models import Activity
from django.contrib.auth.models import User
from django.utils import timezone

# Get a user
user = User.objects.first()

# Check activities
activities = Activity.objects.filter(user=user).order_by('-activity_date')
for a in activities:
    print(f"{a.name}: {a.activity_date} (TZ-aware: {timezone.is_aware(a.activity_date)})")

# Check today's range calculation
now = timezone.now()
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
print(f"Today range: {today_start} to {today_end}")
print(f"Now: {now}")

# Query today's activities
today_activities = Activity.objects.filter(
    user=user,
    activity_date__gte=today_start,
    activity_date__lte=today_end
)
print(f"Found {today_activities.count()} activities for today")
```

### Database Direct Query
```bash
python manage.py dbshell

SELECT id, name, activity_date, created_at 
FROM energy_tracker_activity 
WHERE user_id = <user_id> 
ORDER BY activity_date DESC 
LIMIT 10;
```

---

## Success Criteria

The bug will be considered identified when:
1. ✅ We can consistently reproduce the issue
2. ✅ We understand the exact code path causing the problem
3. ✅ We can explain why activities logged earlier in the day don't appear on homepage
4. ✅ We can explain why they appear in the wrong history section
5. ✅ We have documented the root cause with evidence

---

## Next Steps After Investigation
Once the root cause is identified, proceed to:
1. Create a detailed fix plan
2. Implement the fix
3. Write regression tests
4. Test thoroughly
5. Document the fix in commit message
