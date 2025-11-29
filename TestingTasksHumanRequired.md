# Testing Tasks Requiring Human Intervention

This document lists tasks from the GitHub Testing Plan that cannot be automated and require human action.

---

## Repository Configuration Tasks

### 1. Configure GitHub Repository Secrets
**Reference:** GitHubTestingPlan.md - Step 2.2

**Action Required:**
1. Navigate to: `https://github.com/Irine-Juliet/Energy-Manager/settings/secrets/actions`
2. Add the following repository secrets:
   - **Name:** `DJANGO_SECRET_KEY`
   - **Value:** Generate using command below, then add to GitHub Secrets

**Command to generate secret key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Optional Secrets (for advanced features):**
- `CODECOV_TOKEN` - For code coverage reporting integration
- `DATABASE_URL` - If using external database
- `RENDER_SERVICE_ID` - For automated deployment
- `RENDER_API_KEY` - For automated deployment

**Status:** ⏳ Pending  
**Priority:** High - Required for CI pipeline to work properly

---

### 2. Set Up Branch Protection Rules
**Reference:** GitHubTestingPlan.md - Step 9.1

**Action Required:**
1. Navigate to: `https://github.com/Irine-Juliet/Energy-Manager/settings/branches`
2. Click "Add rule" or "Add branch protection rule"
3. Branch name pattern: `main`
4. Enable the following settings:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select required status checks:
     - `lint`
     - `django-checks`
     - `migrations`
     - `test (3.10)`
     - `test (3.11)`
     - `test (3.12)`
   - ✅ Require pull request reviews before merging (optional but recommended)
   - ✅ Dismiss stale pull request approvals when new commits are pushed
5. Save changes

**Status:** ⏳ Pending  
**Priority:** High - Protects main branch from broken code

---

### 3. Enable GitHub Actions Notifications
**Reference:** GitHubTestingPlan.md - Step 9.1

**Action Required:**
1. Navigate to: `https://github.com/settings/notifications`
2. Scroll to "Actions" section
3. Enable the following:
   - ✅ Email notifications for failed workflows
   - ✅ Email notifications for workflow run approvals
4. Configure email preferences

**Status:** ⏳ Pending  
**Priority:** Medium - Helps stay informed about CI failures

---

## Optional Advanced Features

### 4. Set Up Codecov Integration (Optional)
**Reference:** GitHubTestingPlan.md - Step 5.1

**Action Required:**
1. Sign up at https://codecov.io with GitHub account
2. Enable Codecov for the Energy-Manager repository
3. Copy the Codecov token
4. Add `CODECOV_TOKEN` to GitHub repository secrets
5. Uncomment the Codecov upload step in `.github/workflows/ci.yml`

**Status:** ⏳ Pending  
**Priority:** Low - Optional but provides better coverage visualization

---

### 5. Create Deployment Workflow (Optional)
**Reference:** GitHubTestingPlan.md - Step 7.1

**Action Required:**
1. Review `.github/workflows/deploy.yml` template in the plan
2. If using Render or another deployment platform:
   - Add deployment service credentials to GitHub Secrets
   - Create deployment workflow file
   - Test deployment process
3. If not deploying via GitHub Actions, skip this step

**Status:** ⏳ Pending  
**Priority:** Low - Only needed if automating deployments

---

### 6. Set Up Scheduled Comprehensive Tests (Optional)
**Reference:** GitHubTestingPlan.md - Step 7.2

**Action Required:**
1. Review the scheduled-tests.yml workflow in the plan
2. Decide if nightly/weekly comprehensive tests are needed
3. If yes, create `.github/workflows/scheduled-tests.yml`
4. Adjust schedule as needed (default: daily at 2 AM UTC)

**Status:** ⏳ Pending  
**Priority:** Low - Useful for larger teams or production apps

---

### 7. Create Security Scan Workflow (Optional)
**Reference:** GitHubTestingPlan.md - Step 6.1

**Action Required:**
1. Review if separate security scanning workflow is needed
2. If yes, create `.github/workflows/security-scan.yml`
3. Schedule for weekly runs (recommended: Sunday at midnight)

**Status:** ⏳ Pending  
**Priority:** Low - Security scanning is already included in main CI

---

## Testing & Validation Tasks

### 8. Test Workflow with Pull Request
**Reference:** GitHubTestingPlan.md - Step 8.2

**Action Required:**
1. Push the current branch to GitHub: `git push origin githubtest-development`
2. Create a pull request from `githubtest-development` to `develop` or `main`
3. Verify that all CI jobs run successfully
4. Review job outputs and logs
5. Check that artifacts are uploaded correctly
6. Download and review coverage reports
7. Ensure PR shows green checkmarks for all required checks

**Status:** ⏳ Pending  
**Priority:** High - Validates entire CI pipeline

---

### 9. Test Failure Scenarios
**Reference:** GitHubTestingPlan.md - Step 8.3

**Action Required:**
After verifying successful workflow:
1. Intentionally introduce a test failure
2. Push and observe how CI handles failures
3. Verify error messages are clear
4. Check that artifacts are uploaded on failure
5. Fix the failure and verify pipeline turns green
6. Test with linting failures as well

**Status:** ⏳ Pending  
**Priority:** Medium - Helps understand failure debugging

---

## Documentation Review Tasks

### 10. Review and Customize Documentation
**Action Required:**
Review the following newly created files and customize as needed:
- `CONTRIBUTING.md` - Development guidelines
- `README.md` - Updated with CI badge and info
- `.github/workflows/README.md` - Workflow documentation
- `.github/README.md` - GitHub folder overview

Make any project-specific adjustments.

**Status:** ⏳ Pending  
**Priority:** Medium - Ensures documentation matches project needs

---

## Future Enhancements (Not Urgent)

### 11. Reorganize Test Files (Optional)
**Reference:** GitHubTestingPlan.md - Step 4.1

**Action Required:**
1. Create `energy_tracker/tests/` directory
2. Split existing tests into separate modules:
   - `test_models.py`
   - `test_views.py`
   - `test_forms.py`
   - `test_utils.py`
   - `test_authentication.py`
   - `test_integration.py`
3. Add test tags for categorization
4. Update imports

**Status:** ⏳ Pending  
**Priority:** Low - Improves organization but tests work as-is

---

### 12. Add Test Tags for Selective Execution (Optional)
**Reference:** GitHubTestingPlan.md - Step 4.2

**Action Required:**
1. Add `@tag` decorators to test classes
2. Use tags: `fast`, `slow`, `unit`, `integration`, `models`, `views`, etc.
3. Update CI workflow to run fast tests first (optional optimization)

**Status:** ⏳ Pending  
**Priority:** Low - Optimization for larger test suites

---

### 13. Create Energy Manager Specific Tests (Optional)
**Reference:** GitHubTestingPlan.md - Step 4.3

**Action Required:**
Review and create additional tests for:
- Energy level validation (-2 to +2 range)
- Dashboard calculation accuracy
- Activity ordering by occurrence time
- Timezone handling (America/New_York)

**Status:** ⏳ Pending  
**Priority:** Low - Additional test coverage

---

## Quick Start Checklist

To get CI pipeline running, complete these tasks in order:

- [ ] **Task 1:** Configure GitHub Secrets (DJANGO_SECRET_KEY)
- [ ] **Task 8:** Push branch and create pull request to test workflow
- [ ] **Task 2:** Set up branch protection rules
- [ ] **Task 9:** Test failure scenarios
- [ ] **Task 3:** Enable GitHub Actions notifications

All other tasks are optional enhancements.

---

## Notes

- All automated implementation tasks have been completed
- Configuration files are in place and ready to use
- The CI workflow will run as soon as code is pushed to GitHub
- Some features (like Codecov) are optional and can be added later
- Review the GitHubTestingPlan.md for detailed explanations of each task

---

**Created:** November 29, 2025  
**Last Updated:** November 29, 2025  
**Status:** Ready for human action
