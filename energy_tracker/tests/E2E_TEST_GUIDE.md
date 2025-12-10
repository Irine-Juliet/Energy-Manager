# End-to-End (E2E) Testing Guide

This guide explains how to set up and run the E2E tests for the Energy Manager application.

## Overview

The E2E tests use Selenium WebDriver to simulate real user interactions with the application in a browser. These tests cover complete user journeys from signup to activity management.

## Prerequisites

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install -r requirements-dev.txt
```

This will install:
- `selenium==4.15.2` - Web automation framework
- `webdriver-manager==4.0.1` - Automatic driver management

### 2. Browser Setup

The tests are configured to use Chrome in headless mode (no visible browser window). The `webdriver-manager` package automatically downloads and manages the ChromeDriver.

**Alternative: Use Firefox**

If you prefer Firefox, modify `conftest.py` to use GeckoDriver:

```python
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

@pytest.fixture(scope='function')
def browser(firefox_options):
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()
```

## Running E2E Tests

### Run All E2E Tests

```bash
pytest -m e2e
```

### Run All E2E Tests with Visible Browser (Non-Headless)

For debugging, you can disable headless mode by modifying the `chrome_options` fixture in `conftest.py`:

```python
@pytest.fixture(scope='function')
def chrome_options():
    options = ChromeOptions()
    # Comment out headless mode
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return options
```

### Run Specific E2E Test

```bash
pytest energy_tracker/tests/test_e2e.py::TestUserJourneyE2E::test_complete_signup_flow -v
```

### Run E2E Tests with Verbose Output

```bash
pytest -m e2e -v -s
```

The `-s` flag shows print statements and browser output.

## E2E Test Coverage

The test suite includes 15 comprehensive E2E tests:

### Authentication & User Management (Tests 1-2)
1. **Complete signup flow** - User registration and auto-login
2. **Login/logout flow** - Authentication and session management

### Activity Management (Tests 3-6)
3. **Log single activity** - Create and verify activity
4. **Log multiple activities** - Batch activity logging
5. **Edit activity** - Update existing activity
6. **Delete activity** - Remove activity with confirmation

### Dashboard & Visualization (Test 7)
7. **Dashboard chart rendering** - Verify Chart.js visualizations

### Search & Filtering (Tests 8-9)
8. **Activity search** - Search by name
9. **Energy level filtering** - Filter by energy level

### UI Interactions (Tests 10-11)
10. **Autocomplete** - Name suggestion feature
11. **Settings theme change** - Dark/light mode toggle

### Responsive & Navigation (Tests 12-13)
12. **Mobile responsive view** - Mobile viewport testing
13. **Pagination** - Multi-page navigation

### Advanced Features (Tests 14-15)
14. **Retrospective logging** - Past-dated activities
15. **Bulk delete** - Multiple activity deletion

## Test Structure

Each E2E test follows this pattern:

1. **Setup** - Create necessary database objects
2. **Login** - Authenticate user via browser
3. **Navigate** - Go to specific page
4. **Interact** - Fill forms, click buttons, etc.
5. **Assert** - Verify expected outcomes
6. **Cleanup** - Automatic (handled by fixtures)

## Common Issues & Troubleshooting

### Issue: "ChromeDriver not found"

**Solution:** The `webdriver-manager` should handle this automatically. If it fails:
- Ensure you have internet connection for initial download
- Manually install ChromeDriver: https://chromedriver.chromium.org/

### Issue: "Element not found" or timeout errors

**Solution:** 
- Increase wait time in `WebDriverWait(browser, 10)` → `WebDriverWait(browser, 20)`
- Check if element selectors match your HTML
- Run in non-headless mode to see what's happening

### Issue: Tests pass locally but fail in CI/CD

**Solution:**
- Ensure CI environment has Chrome/Chromium installed
- Use headless mode in CI
- Add longer wait times for slower CI environments

### Issue: "Database is locked" errors

**Solution:**
- Use `@pytest.mark.django_db(transaction=True)` for E2E tests
- This is already configured in `test_e2e.py`

## Debugging E2E Tests

### Take Screenshots on Failure

Add this to your test:

```python
try:
    # Your test code
    assert condition
except AssertionError:
    browser.save_screenshot('failure_screenshot.png')
    raise
```

### Add Breakpoints

```python
import pdb; pdb.set_trace()
# or
import ipdb; ipdb.set_trace()  # if you have ipdb installed
```

### Print Page Source

```python
print(browser.page_source)
```

### Check Console Logs

```python
logs = browser.get_log('browser')
print(logs)
```

## Best Practices

1. **Use Explicit Waits** - Always use `WebDriverWait` instead of `time.sleep()`
2. **Isolate Tests** - Each test should be independent
3. **Clean Up** - Fixtures handle cleanup automatically
4. **Meaningful Assertions** - Assert multiple conditions to catch regressions
5. **Page Objects** - For larger test suites, consider Page Object Model pattern

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run E2E tests
        run: pytest -m e2e --headless
```

## Performance Considerations

- **E2E tests are slow** (~30-60 seconds per test)
- Run E2E tests separately: `pytest -m "not e2e"` for quick tests
- Use `pytest-xdist` for parallel execution: `pytest -m e2e -n auto`

## Next Steps

1. **Expand Coverage** - Add more edge cases as features evolve
2. **Visual Testing** - Consider adding screenshot comparison tests
3. **Cross-Browser** - Test on Firefox, Safari, Edge
4. **Accessibility** - Add tests using axe-core or similar tools

## Resources

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)
- [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager)

---

**Last Updated:** November 29, 2025  
**Test Count:** 15 E2E tests  
**Estimated Runtime:** ~8-15 minutes
