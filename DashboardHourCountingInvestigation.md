# Dashboard Hour Counting Investigation Plan

## Bug Summary
The "Time per Energy State" graph on the dashboard displays incorrect hour counts, showing 1 hour per activity instead of summing the actual duration values from logged activities.

## Investigation Objectives
1. Identify where the dashboard graph data is calculated
2. Determine why duration values are being ignored
3. Locate the root cause of the counting logic error
4. Verify if the bug affects all energy states consistently
5. Assess whether the issue is in data aggregation, database query, or frontend rendering

---

## Research Plan

### Phase 1: Code Architecture Review
**Goal:** Understand the data flow from activity logging to dashboard display

#### Step 1.1: Identify Dashboard View Logic
- [ ] Locate the dashboard view function/class in `energy_tracker/views.py`
- [ ] Identify how activity data is queried from the database
- [ ] Document the query logic used for aggregating time per energy state
- [ ] Check if the view uses raw SQL, ORM aggregation, or manual iteration

#### Step 1.2: Examine Activity Model
- [ ] Review `energy_tracker/models.py` for the Activity model structure
- [ ] Verify the `duration` field exists and its data type
- [ ] Check if there are any model methods that calculate time/duration
- [ ] Confirm the `energy_level` field structure and possible values

#### Step 1.3: Review Dashboard Template
- [ ] Examine the dashboard template in `templates/energy_tracker/dashboard.html`
- [ ] Identify how graph data is passed from backend to frontend
- [ ] Check if any JavaScript/chart library is processing the data
- [ ] Verify if data transformation happens client-side

### Phase 2: Data Aggregation Analysis
**Goal:** Pinpoint the exact location where hours are being miscounted

#### Step 2.1: Trace Data Query Logic
- [ ] Search for aggregation functions (Sum, Count, etc.) in views.py
- [ ] Look for queries filtering activities by energy_level
- [ ] Check if `.count()` is being used instead of `.aggregate(Sum('duration'))`
- [ ] Review any helper functions in `energy_tracker/utils.py` related to time calculation

#### Step 2.2: Database Schema Verification
- [ ] Review migration files to confirm duration field was properly added
- [ ] Check if duration has a default value that might interfere
- [ ] Verify data types (IntegerField, FloatField, DurationField, etc.)
- [ ] Confirm there are no database-level constraints affecting the field

#### Step 2.3: Sample Data Testing
- [ ] Query the database directly to verify duration values are stored correctly
- [ ] Check if logged activities have non-null, non-zero duration values
- [ ] Verify energy_level values are being stored as expected
- [ ] Test a manual aggregation query to confirm expected behavior

### Phase 3: Logic Flow Debugging
**Goal:** Understand the complete calculation pipeline

#### Step 3.1: Frontend-Backend Integration
- [ ] Identify the exact JSON/context data structure passed to the template
- [ ] Check if serialization is dropping or transforming duration data
- [ ] Verify chart library configuration and data format requirements
- [ ] Test if the issue occurs when passing different data structures

#### Step 3.2: Edge Case Analysis
- [ ] Check handling of activities with zero duration
- [ ] Verify behavior with activities spanning multiple hours
- [ ] Test with fractional hour durations (e.g., 0.5, 1.5 hours)
- [ ] Confirm behavior across all energy states (-2 to +2)

#### Step 3.3: Recent Changes Review
- [ ] Check git history for recent changes to dashboard view
- [ ] Review any recent migrations affecting Activity model
- [ ] Look for changes to duration field implementation
- [ ] Identify if this is a regression or original implementation issue

### Phase 4: Root Cause Hypothesis Testing
**Goal:** Validate the most likely causes

#### Hypothesis 1: Using COUNT instead of SUM
- [ ] Search for `.count()` usage in dashboard aggregation logic
- [ ] Verify if query results in activity count vs. duration sum
- [ ] Expected symptom: Exactly matches bug description (1 per activity)

#### Hypothesis 2: Duration Field Not Included in Query
- [ ] Check if queryset selects duration field
- [ ] Verify if only() or values() is limiting fields
- [ ] Expected symptom: Duration always defaults to 1

#### Hypothesis 3: Frontend Data Processing Error
- [ ] Check if chart library expects different data format
- [ ] Verify if JavaScript is transforming the data incorrectly
- [ ] Expected symptom: Backend data correct, frontend display wrong

#### Hypothesis 4: Default Value Override
- [ ] Check if duration defaults to 1 in model or form
- [ ] Verify if missing duration values are set to 1 somewhere
- [ ] Expected symptom: Some activities show correct duration, others default to 1

### Phase 5: Validation and Testing
**Goal:** Confirm the root cause and verify the fix scope

#### Step 5.1: Create Test Cases
- [ ] Write unit test for duration aggregation by energy level
- [ ] Create integration test for dashboard data calculation
- [ ] Add edge case tests (zero duration, large values, fractional hours)

#### Step 5.2: Fix Impact Assessment
- [ ] Identify all views/functions that might have similar issues
- [ ] Check if activity_history view has the same problem
- [ ] Verify if any other dashboard metrics are affected
- [ ] Document all locations requiring fixes

#### Step 5.3: Data Integrity Check
- [ ] Verify existing activity data has correct duration values
- [ ] Check if any data migration is needed post-fix
- [ ] Confirm no data corruption occurred

---

## Key Files to Investigate
1. `energy_tracker/views.py` - Dashboard view and data aggregation logic
2. `energy_tracker/models.py` - Activity model with duration field
3. `templates/energy_tracker/dashboard.html` - Graph rendering template
4. `energy_tracker/utils.py` - Helper functions for calculations
5. Migration files - Duration field implementation history
6. `energy_tracker/tests.py` - Existing tests for dashboard functionality

## Expected Findings
Based on the bug description, the most likely root cause is:
- The dashboard view is using `.count()` to count activities instead of `.aggregate(Sum('duration'))` to sum duration values
- This would result in each activity contributing 1 to the total regardless of actual duration

## Success Criteria
- Identified the exact line(s) of code causing the miscounting
- Understood why duration is being ignored in calculations
- Documented the complete fix scope including all affected components
- Created reproducible test cases demonstrating the bug

## Timeline Estimate
- Phase 1: 30 minutes
- Phase 2: 45 minutes
- Phase 3: 30 minutes
- Phase 4: 45 minutes
- Phase 5: 30 minutes
- **Total: ~3 hours**

---

## Notes & Observations
_This section will be updated during investigation with findings, code snippets, and insights._

