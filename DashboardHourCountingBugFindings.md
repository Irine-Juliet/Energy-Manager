# Dashboard Hour Counting Bug - Investigation Findings & Fix Plan

**Investigation Date:** November 29, 2025  
**Bug Location:** `energy_tracker/views.py` - `dashboard_view()` function  
**Severity:** High - Incorrect data visualization affecting user insights

---

## Executive Summary

The "Time per Energy State" graph on the dashboard displays **incorrect hour counts** because the current implementation counts the number of **hour slots** with activities rather than summing the actual **duration** of activities. This results in each hour slot contributing 1 to the total regardless of how much time was actually spent in that energy state.

### Actual vs Expected Behavior

**Current (Buggy) Behavior:**
- Energy level -2: 3 hours (counting 3 hour slots)
- Energy level -1: 2 hours (counting 2 hour slots)
- Energy level 1: 3 hours (counting 3 hour slots)
- Energy level 2: 5 hours (counting 5 hour slots)

**Expected (Correct) Behavior:**
- Energy level -2: 4.07 hours (sum of all -2 activity durations)
- Energy level -1: 2.00 hours (sum of all -1 activity durations)
- Energy level 1: 10.42 hours (sum of all 1 activity durations)
- Energy level 2: 8.25 hours (sum of all 2 activity durations)

---

## Root Cause Analysis

### Problem Location

**File:** `energy_tracker/views.py`  
**Function:** `dashboard_view()`  
**Lines:** 160-174

### Flawed Implementation

The current code uses an **indirect aggregation approach** that fundamentally misunderstands the data model:

```python
# Current BUGGY implementation (lines 153-174)
hourly_avg = []
for hour in range(24):
    q = today_activities.filter(activity_date__hour=hour)
    avg_val = q.aggregate(Avg('energy_level'))['energy_level__avg']
    hourly_avg.append(float(avg_val) if avg_val is not None else None)

# Count how many hours (distinct hour slots) fall into each category.
hours_per_category = {'-2': 0, '-1': 0, '0': 0, '1': 0, '2': 0}
categories = [-2, -1, 0, 1, 2]
for avg in hourly_avg:
    if avg is None:
        continue
    # Find the nearest category by absolute distance
    try:
        nearest = min(categories, key=lambda c: abs(avg - c))
        hours_per_category[str(int(nearest))] += 1  # <-- BUG: adds 1 per hour slot
    except Exception:
        hours_per_category['0'] += 1
```

### Why This Approach is Fundamentally Flawed

1. **Conceptual Mismatch**: The code treats each hour slot (0-23) as a single unit worth 1 hour, ignoring the fact that multiple activities can occur in the same hour and that activities have varying durations.

2. **Data Loss**: The aggregation first computes hourly averages, which loses all duration information. The `duration` field is never consulted.

3. **Incorrect Mapping**: Activities are mapped to hour slots based on their `activity_date` (start time), then each occupied hour slot is counted as 1 hour, regardless of:
   - How many activities occurred in that hour
   - How long each activity lasted
   - Whether activities spanned multiple hours

4. **Energy Level Averaging**: The code averages energy levels within each hour, which further distorts the data. If an hour has both a -2 activity (60 minutes) and a +2 activity (5 minutes), they're treated equally in the average.

### Example Demonstrating the Bug

Consider these activities:
- Activity A: "Deep work session" - 180 minutes (3 hours), energy level = 2, starts at 9:00 AM
- Activity B: "Quick email check" - 5 minutes, energy level = -1, starts at 9:30 AM

**Current buggy logic:**
- Hour slot 9 contains both activities
- Average energy for hour 9 = (2 + -1) / 2 = 0.5
- Nearest category = 1 (somewhat energizing)
- Result: 1 hour counted for energy level 1

**Correct logic should be:**
- Energy level 2: 3 hours (from 180 minutes of deep work)
- Energy level -1: 0.08 hours (from 5 minutes of email)

The bug causes a **massive distortion**: instead of correctly attributing 3 hours to "very energizing" and 0.08 hours to "somewhat draining", it incorrectly attributes 1 hour to "somewhat energizing".

---

## Database Investigation Results

### Data Integrity Check ✅

The database contains **correct duration values** stored in minutes:

```
Sample activities with durations:
  - testing: 60 minutes (Energy: 2)
  - testing in the past: 180 minutes (Energy: -2)
  - testing in the past: 360 minutes (Energy: 1)
  - testing very in the past: 300 minutes (Energy: 2)
  - coded a lot: 60 minutes (Energy: 2)
  - texted someone i like: 15 minutes (Energy: 2)
  - had dinner: 60 minutes (Energy: 1)
  - coded a lot: 60 minutes (Energy: 2)
  - saw a problem with format: 4 minutes (Energy: -2)
  - tested results: 60 minutes (Energy: -2)
```

### Activity Model ✅

The `Activity` model correctly defines the `duration` field:

```python
duration = models.PositiveIntegerField(
    default=60,
    validators=[MinValueValidator(1), MaxValueValidator(1440)],
    help_text='Duration in minutes (1-1440)'
)
```

### Issue is NOT in:
- ✅ Database schema (duration field exists and works correctly)
- ✅ Data entry (activities are logged with proper duration values)
- ✅ Activity model (model structure is correct)
- ✅ Frontend rendering (template correctly displays backend data)

### Issue IS in:
- ❌ **Dashboard view aggregation logic** (lines 160-174 in `views.py`)

---

## Impact Assessment

### Affected Components

1. **Primary Impact:**
   - Dashboard "Time per Energy State" bar chart - **completely incorrect**
   - Dashboard insights panel - shows wrong hour counts when hovering over bars

2. **NOT Affected:**
   - Activity logging functionality - works correctly
   - Activity history view - displays correct data
   - Other dashboard metrics (today's average, energy flow chart, etc.)
   - Database data integrity - all data is stored correctly

### User Impact

- **High severity** for users relying on the dashboard for time management insights
- Users may make incorrect decisions about energy allocation based on wrong data
- Undermines trust in the application's analytics capabilities
- Particularly problematic for activities with long durations (multi-hour sessions)

---

## Fix Plan

### Approach: Direct Duration Aggregation

Replace the flawed hour-slot counting logic with a **direct aggregation** of activity durations by energy level.

### Implementation Steps

#### Step 1: Replace the buggy logic

**Remove:** Lines 153-174 (entire hourly averaging and hour-slot counting logic)

**Replace with:** Direct duration aggregation using Django ORM:

```python
# Calculate total time (in hours) spent in each energy state today
from django.db.models import Sum

hours_per_category = {'-2': 0, '-1': 0, '0': 0, '1': 0, '2': 0}
categories = [-2, -1, 0, 1, 2]

for category in categories:
    total_minutes = today_activities.filter(
        energy_level=category
    ).aggregate(
        total=Sum('duration')
    )['total'] or 0
    
    # Convert minutes to hours (rounded to 2 decimal places)
    hours_per_category[str(category)] = round(total_minutes / 60.0, 2)
```

#### Step 2: Update context variable

No changes needed - the context variable `hours_per_category` is already correctly passed to the template.

#### Step 3: Verify frontend compatibility

The frontend JavaScript in `dashboard.html` expects the same data structure, so no frontend changes are required.

### Code Changes Required

**File:** `energy_tracker/views.py`

**Location:** `dashboard_view()` function, lines 153-174

**Change Type:** Replace existing logic

**Lines to remove:** 21 lines

**Lines to add:** ~13 lines

**Net change:** -8 lines (simplification)

---

## Testing Strategy

### Unit Tests to Add

1. **Test duration aggregation accuracy:**
   ```python
   def test_dashboard_hours_per_category_sums_duration(self):
       """Verify that hours_per_category sums actual activity durations"""
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
       
       response = self.client.get('/dashboard/')
       hours_data = json.loads(response.context['hours_per_category'])
       
       self.assertEqual(hours_data['2'], 3.0)
       self.assertEqual(hours_data['-1'], 0.25)
   ```

2. **Test multiple activities same energy level:**
   ```python
   def test_dashboard_aggregates_multiple_activities_same_level(self):
       """Verify that multiple activities with same energy level are summed"""
       # Create 3 activities with energy level 2
       for i in range(3):
           Activity.objects.create(
               user=self.user,
               name=f"Activity {i}",
               duration=60,  # 1 hour each
               energy_level=2,
               activity_date=timezone.now()
           )
       
       response = self.client.get('/dashboard/')
       hours_data = json.loads(response.context['hours_per_category'])
       
       self.assertEqual(hours_data['2'], 3.0)  # 3 hours total
   ```

3. **Test activities in same hour slot:**
   ```python
   def test_dashboard_handles_multiple_activities_same_hour(self):
       """Verify correct behavior when multiple activities occur in same hour"""
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
       
       response = self.client.get('/dashboard/')
       hours_data = json.loads(response.context['hours_per_category'])
       
       self.assertEqual(hours_data['2'], 2.0)
       self.assertEqual(hours_data['-2'], 0.5)
   ```

### Manual Testing Checklist

- [ ] Create activities with varying durations (15 min, 1 hour, 3 hours, etc.)
- [ ] Verify dashboard bar chart shows correct hour totals
- [ ] Check that fractional hours are displayed correctly (e.g., 1.5 hours)
- [ ] Test with activities spanning different energy levels
- [ ] Verify insights panel shows correct hour counts on hover
- [ ] Test edge cases:
  - [ ] Zero activities (all bars should be 0)
  - [ ] Single activity per energy level
  - [ ] Multiple activities in same hour slot
  - [ ] Activities with very short durations (1-5 minutes)
  - [ ] Activities with very long durations (6-8 hours)

### Regression Testing

- [ ] Verify other dashboard metrics still work correctly
- [ ] Check that activity logging still functions properly
- [ ] Ensure activity history view is unaffected
- [ ] Test dashboard performance with large datasets

---

## Additional Improvements (Optional)

### Enhancement 1: Display format for fractional hours

Consider updating the frontend to display fractional hours more intuitively:
- "1.5 hours" → "1h 30m"
- "0.25 hours" → "15m"

**Location:** `templates/energy_tracker/dashboard.html`, line ~210 in `updateInsights()` function

### Enhancement 2: Include neutral activities

The current implementation excludes energy level 0 (neutral) activities from the graph. Consider whether these should be included in the visualization.

### Enhancement 3: Remove now-unused hourly_avg calculation

After fixing the bug, the `hourly_avg` variable (lines 153-159) is only used for other parts of the dashboard. Verify if it's still needed or can be removed/refactored.

**Current usage:** Passed to frontend as `hourly_avg` in context (line 191)

---

## Timeline Estimate

- **Code fix:** 15 minutes
- **Unit test creation:** 45 minutes
- **Manual testing:** 30 minutes
- **Code review & QA:** 30 minutes
- **Total:** ~2 hours

---

## Risk Assessment

### Risk Level: **Low**

**Justification:**
- Simple, isolated fix in a single function
- No database migrations required
- No changes to data model
- Frontend compatibility maintained
- Easy to verify with automated tests

### Rollback Plan

If issues arise, the fix can be easily reverted by restoring the original lines 153-174 from git history.

---

## References

### Related Files
- `energy_tracker/views.py` - Contains buggy code
- `energy_tracker/models.py` - Activity model with duration field
- `templates/energy_tracker/dashboard.html` - Frontend visualization
- `energy_tracker/tests.py` - Location for new tests

### Git Information
- **Repository:** Energy-Manager (Irine-Juliet)
- **Current Branch:** bug-fix-for-history-and-log-activity
- **Affected Function:** `dashboard_view()` in `energy_tracker/views.py`

### Related Documentation
- Investigation plan: `DashboardHourCountingInvestigation.md`
- Activity model specification: See `energy_tracker/models.py` lines 10-75

---

## Conclusion

The bug is caused by a fundamental misunderstanding of the data aggregation requirements. The current implementation treats hour slots as the unit of measurement rather than actual activity durations. The fix is straightforward: directly aggregate activity durations by energy level using Django's `Sum()` aggregation function.

**Confidence Level:** Very High (100%)
- Root cause clearly identified
- Database investigation confirms correct data storage
- Reproduction steps validated with sample data
- Fix approach tested with Python snippet (see investigation results)

**Next Steps:**
1. Implement the fix in `energy_tracker/views.py`
2. Add comprehensive unit tests
3. Perform manual testing
4. Submit pull request for code review
5. Deploy to production after approval
