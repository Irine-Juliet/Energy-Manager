# GitHub Actions Testing Best Practices for Django Applications

## Overview

This document outlines best practices for implementing automated testing with GitHub Actions for the Energy Manager application - a Django 5.0 server-side rendered multi-page application with SQLite database, user authentication, and data analytics features.

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Workflow Structure](#workflow-structure)
3. [Environment Configuration](#environment-configuration)
4. [Testing Strategy](#testing-strategy)
5. [Security Best Practices](#security-best-practices)
6. [Performance Optimization](#performance-optimization)
7. [Advanced Patterns](#advanced-patterns)
8. [Sample Workflow Files](#sample-workflow-files)
9. [Troubleshooting Guide](#troubleshooting-guide)

---

## Core Principles

### 1. **Fast Feedback Loop**
- Run tests on every push and pull request
- Fail fast: run quick checks (linting, syntax) before expensive tests
- Use matrix testing to parallelize across Python versions
- Cache dependencies to reduce build time

### 2. **Comprehensive Coverage**
- Unit tests for models, forms, and utility functions
- Integration tests for views and request/response flows
- Database migration testing
- Template rendering validation
- Static file collection verification

### 3. **Isolation & Reproducibility**
- Use fresh database for each test run
- Clean environment setup with no side effects
- Pin dependencies to specific versions
- Document all environment variables

### 4. **Visibility & Debugging**
- Upload test results as artifacts
- Generate and store coverage reports
- Provide clear failure messages
- Track test performance over time

---

## Workflow Structure

### Basic Workflow Organization

```
.github/
└── workflows/
    ├── ci.yml                    # Main CI pipeline (runs on push/PR)
    ├── scheduled-tests.yml       # Nightly/weekly comprehensive tests
    ├── security-scan.yml         # Security vulnerability scanning
    └── deploy.yml                # Deployment workflow (post-merge)
```

### Recommended Triggers

**For Django Applications:**

```yaml
on:
  # Trigger on push to main and feature branches
  push:
    branches: [ main, develop, 'feature/**', 'bugfix/**' ]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.gitignore'
  
  # Trigger on pull requests
  pull_request:
    branches: [ main, develop ]
  
  # Manual trigger
  workflow_dispatch:
  
  # Scheduled runs (e.g., nightly)
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
```

---

## Environment Configuration

### 1. **Python Version Strategy**

**For Django 5.0 Applications:**

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    os: [ubuntu-latest]
  fail-fast: false  # Don't cancel other jobs if one fails
```

**Rationale:**
- Django 5.0 requires Python 3.10+
- Test on multiple Python versions to ensure compatibility
- Ubuntu is recommended for Django testing (matches production)
- `fail-fast: false` allows seeing all version failures

### 2. **Database Configuration**

**For SQLite-based Django Apps:**

```yaml
env:
  DATABASE_URL: 'sqlite:///test_db.sqlite3'
  SECRET_KEY: 'test-secret-key-for-ci-only-not-production'
  DEBUG: 'False'
  ALLOWED_HOSTS: 'localhost,127.0.0.1'
```

**For PostgreSQL Compatibility Testing:**

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
      POSTGRES_DB: test_db
    ports:
      - 5432:5432
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

### 3. **Environment Variables**

**Required for Energy Manager:**

```yaml
env:
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
  DEBUG: 'False'
  ALLOWED_HOSTS: 'localhost,127.0.0.1'
  DATABASE_URL: 'sqlite:///test_db.sqlite3'
  TZ: 'America/New_York'  # Match production timezone
```

**Using GitHub Secrets:**
- Store sensitive data in repository secrets
- Never hardcode production credentials
- Use different secrets for staging/production

---

## Testing Strategy

### 1. **Multi-Stage Testing Pipeline**

**Recommended Order:**

```yaml
jobs:
  # Stage 1: Fast checks (< 1 minute)
  lint-and-format:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Check syntax errors
      - Run Ruff linting
      - Check formatting
      - Verify imports

  # Stage 2: Unit tests (2-5 minutes)
  unit-tests:
    name: Unit Tests
    needs: lint-and-format
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - Run model tests
      - Run form tests
      - Run utility tests

  # Stage 3: Integration tests (5-10 minutes)
  integration-tests:
    name: Integration Tests
    needs: unit-tests
    runs-on: ubuntu-latest
    steps:
      - Run view tests
      - Test authentication flows
      - Test database queries
      - Verify templates

  # Stage 4: System tests (5-15 minutes)
  system-tests:
    name: System & Migration Tests
    needs: integration-tests
    runs-on: ubuntu-latest
    steps:
      - Test database migrations
      - Collect static files
      - Run full test suite
      - Generate coverage report
```

### 2. **Django-Specific Testing**

**Running Django Tests:**

```yaml
- name: Run Django Tests
  run: |
    python manage.py test --verbosity=2 --parallel=auto
  env:
    SECRET_KEY: 'test-key'
    DEBUG: 'False'
```

**With Coverage:**

```yaml
- name: Run Tests with Coverage
  run: |
    coverage run --source='.' manage.py test
    coverage report --show-missing
    coverage xml
    coverage html

- name: Upload Coverage Reports
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    flags: unittests
    fail_ci_if_error: true
```

**Migration Testing:**

```yaml
- name: Check Migrations
  run: |
    python manage.py makemigrations --check --dry-run --no-input
    python manage.py migrate --no-input
    python manage.py check --deploy
```

**Static Files Testing:**

```yaml
- name: Collect Static Files
  run: |
    python manage.py collectstatic --no-input --clear
```

### 3. **Test Organization**

**For Energy Manager Structure:**

```yaml
- name: Run Specific Test Suites
  run: |
    # Run all tests
    python manage.py test
    
    # Run specific app tests
    python manage.py test energy_tracker
    
    # Run specific test classes
    python manage.py test energy_tracker.tests.ActivityModelTests
    
    # Run with specific settings
    python manage.py test --settings=energy_manager.settings_test
```

---

## Security Best Practices

### 1. **Dependency Scanning**

```yaml
- name: Install Safety
  run: pip install safety

- name: Check for Security Vulnerabilities
  run: safety check --json

- name: Audit Dependencies
  run: pip-audit
```

### 2. **Secrets Management**

**Never Do:**
```yaml
env:
  SECRET_KEY: 'django-insecure-actual-secret'  # ❌ NEVER
```

**Always Do:**
```yaml
env:
  SECRET_KEY: ${{ secrets.DJANGO_SECRET_KEY }}  # ✅ CORRECT
```

**Setting up Secrets:**
1. Go to Repository Settings → Secrets and Variables → Actions
2. Add secrets:
   - `DJANGO_SECRET_KEY`
   - `DATABASE_URL` (if using external DB)
   - Any API keys or credentials

### 3. **Permission Restrictions**

```yaml
permissions:
  contents: read  # Read-only access to repository
  pull-requests: write  # For commenting on PRs
  checks: write  # For publishing test results
```

---

## Performance Optimization

### 1. **Dependency Caching**

**Method 1: Using setup-python with cache**

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'
    cache-dependency-path: 'requirements.txt'

- name: Install Dependencies
  run: pip install -r requirements.txt
```

**Method 2: Manual caching for more control**

```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-

- name: Install Dependencies
  run: pip install -r requirements.txt
```

**Caching Database Migrations:**

```yaml
- name: Cache Django Migrations
  uses: actions/cache@v4
  with:
    path: |
      */migrations/*.py
      db.sqlite3
    key: ${{ runner.os }}-migrations-${{ hashFiles('*/migrations/*.py') }}
```

### 2. **Parallel Testing**

```yaml
- name: Run Tests in Parallel
  run: |
    python manage.py test --parallel=auto --verbosity=2
```

### 3. **Test Splitting**

```yaml
strategy:
  matrix:
    test-group: [models, views, forms, integration]

steps:
  - name: Run Test Group
    run: |
      case ${{ matrix.test-group }} in
        models)
          python manage.py test energy_tracker.tests.test_models
          ;;
        views)
          python manage.py test energy_tracker.tests.test_views
          ;;
        forms)
          python manage.py test energy_tracker.tests.test_forms
          ;;
        integration)
          python manage.py test energy_tracker.tests.test_integration
          ;;
      esac
```

---

## Advanced Patterns

### 1. **Reusable Workflows**

**`.github/workflows/reusable-django-tests.yml`:**

```yaml
name: Reusable Django Test Workflow

on:
  workflow_call:
    inputs:
      python-version:
        required: true
        type: string
      django-settings:
        required: false
        type: string
        default: 'energy_manager.settings'
    secrets:
      SECRET_KEY:
        required: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
          cache: 'pip'
      
      - name: Install Dependencies
        run: pip install -r requirements.txt
      
      - name: Run Tests
        run: python manage.py test
        env:
          DJANGO_SETTINGS_MODULE: ${{ inputs.django-settings }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
```

**Using the reusable workflow:**

```yaml
jobs:
  test-py310:
    uses: ./.github/workflows/reusable-django-tests.yml
    with:
      python-version: '3.10'
    secrets:
      SECRET_KEY: ${{ secrets.DJANGO_SECRET_KEY }}
```

### 2. **Conditional Execution**

```yaml
- name: Run Full Test Suite
  if: github.event_name == 'pull_request' || github.ref == 'refs/heads/main'
  run: python manage.py test

- name: Run Quick Tests Only
  if: github.event_name == 'push' && github.ref != 'refs/heads/main'
  run: python manage.py test --tag=fast
```

### 3. **Matrix Exclusions**

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    django-version: ['4.2', '5.0']
    exclude:
      # Django 5.0 requires Python 3.10+
      - python-version: '3.9'
        django-version: '5.0'
```

### 4. **Test Result Publishing**

```yaml
- name: Run Tests with JUnit Output
  run: |
    pip install pytest pytest-django
    pytest --junitxml=junit/test-results.xml

- name: Publish Test Results
  uses: EnricoMi/publish-unit-test-result-action@v2
  if: always()
  with:
    files: junit/test-results.xml
    check_name: Test Results
    comment_mode: always
```

### 5. **Artifact Management**

```yaml
- name: Upload Test Artifacts
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: test-results-${{ matrix.python-version }}
    path: |
      junit/test-results.xml
      htmlcov/
      coverage.xml
      .coverage
    retention-days: 30
```

---

## Sample Workflow Files

### Complete CI Workflow for Energy Manager

**`.github/workflows/ci.yml`:**

```yaml
name: Django CI Pipeline

on:
  push:
    branches: [ main, develop, 'feature/**', 'bugfix/**' ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:

env:
  PYTHON_VERSION: '3.12'
  SECRET_KEY: 'test-secret-key-for-ci-do-not-use-in-production'
  DEBUG: 'False'
  ALLOWED_HOSTS: 'localhost,127.0.0.1'
  TZ: 'America/New_York'

jobs:
  # Job 1: Code Quality Checks
  lint:
    name: Code Quality & Linting
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install Linting Tools
        run: |
          python -m pip install --upgrade pip
          pip install ruff black flake8 isort
      
      - name: Run Ruff Linting
        run: ruff check . --output-format=github
        continue-on-error: false
      
      - name: Check Code Formatting (Black)
        run: black --check --diff .
        continue-on-error: true
      
      - name: Check Import Sorting (isort)
        run: isort --check-only --diff .
        continue-on-error: true
      
      - name: Run Flake8
        run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        continue-on-error: true

  # Job 2: Security Scanning
  security:
    name: Security Vulnerability Scan
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install safety pip-audit
      
      - name: Run Safety Check
        run: safety check --json
        continue-on-error: true
      
      - name: Run Pip Audit
        run: pip-audit
        continue-on-error: true

  # Job 3: Django System Checks
  django-checks:
    name: Django System Checks
    runs-on: ubuntu-latest
    needs: lint
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run Django System Check
        run: python manage.py check --deploy
        env:
          SECRET_KEY: ${{ env.SECRET_KEY }}
      
      - name: Check for Migration Issues
        run: python manage.py makemigrations --check --dry-run --no-input
        env:
          SECRET_KEY: ${{ env.SECRET_KEY }}

  # Job 4: Database Migrations
  migrations:
    name: Test Database Migrations
    runs-on: ubuntu-latest
    needs: django-checks
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run Migrations
        run: python manage.py migrate --no-input
        env:
          SECRET_KEY: ${{ env.SECRET_KEY }}
          DATABASE_URL: 'sqlite:///test_db.sqlite3'
      
      - name: Create Superuser (Test)
        run: |
          python manage.py shell -c "
          from django.contrib.auth import get_user_model;
          User = get_user_model();
          User.objects.create_superuser('admin', 'admin@test.com', 'testpass123')
          "
        env:
          SECRET_KEY: ${{ env.SECRET_KEY }}

  # Job 5: Unit & Integration Tests
  test:
    name: Run Tests (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    needs: migrations
    
    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install coverage pytest pytest-django
      
      - name: Run Migrations
        run: python manage.py migrate --no-input
        env:
          SECRET_KEY: ${{ env.SECRET_KEY }}
      
      - name: Run Tests with Coverage
        run: |
          coverage run --source='.' manage.py test --verbosity=2 --parallel=auto
          coverage report --show-missing
          coverage xml
          coverage html
        env:
          SECRET_KEY: ${{ env.SECRET_KEY }}
      
      - name: Upload Coverage Reports
        uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.12'
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: false
      
      - name: Upload Coverage HTML
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-report-${{ matrix.python-version }}
          path: htmlcov/
          retention-days: 30
      
      - name: Upload Test Database
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: test-database-${{ matrix.python-version }}
          path: db.sqlite3
          retention-days: 7

  # Job 6: Static Files Collection
  static-files:
    name: Collect Static Files
    runs-on: ubuntu-latest
    needs: lint
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Collect Static Files
        run: python manage.py collectstatic --no-input --clear
        env:
          SECRET_KEY: ${{ env.SECRET_KEY }}
      
      - name: Upload Static Files
        uses: actions/upload-artifact@v4
        with:
          name: static-files
          path: staticfiles/
          retention-days: 7

  # Job 7: Build Summary
  summary:
    name: CI Summary
    runs-on: ubuntu-latest
    needs: [lint, security, django-checks, migrations, test, static-files]
    if: always()
    
    steps:
      - name: Check All Jobs Status
        run: |
          echo "Lint: ${{ needs.lint.result }}"
          echo "Security: ${{ needs.security.result }}"
          echo "Django Checks: ${{ needs.django-checks.result }}"
          echo "Migrations: ${{ needs.migrations.result }}"
          echo "Tests: ${{ needs.test.result }}"
          echo "Static Files: ${{ needs.static-files.result }}"
      
      - name: Fail if Required Jobs Failed
        if: |
          needs.lint.result == 'failure' ||
          needs.django-checks.result == 'failure' ||
          needs.migrations.result == 'failure' ||
          needs.test.result == 'failure'
        run: exit 1
```

### Scheduled Comprehensive Testing

**`.github/workflows/scheduled-tests.yml`:**

```yaml
name: Scheduled Comprehensive Tests

on:
  schedule:
    # Run every day at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  comprehensive-test:
    name: Full Test Suite + Performance Benchmarks
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-django pytest-benchmark
      
      - name: Run Full Test Suite
        run: |
          python manage.py test --verbosity=2 --parallel=auto
        env:
          SECRET_KEY: 'test-secret-key'
      
      - name: Run Performance Tests
        run: |
          pytest energy_tracker/tests/test_performance.py --benchmark-only
        continue-on-error: true
      
      - name: Generate Test Report
        run: |
          python manage.py test --verbosity=3 > test_report.txt
        env:
          SECRET_KEY: 'test-secret-key'
        continue-on-error: true
      
      - name: Upload Test Report
        uses: actions/upload-artifact@v4
        with:
          name: nightly-test-report
          path: test_report.txt
          retention-days: 90
```

---

## Troubleshooting Guide

### Common Issues & Solutions

#### 1. **Import Errors**

**Problem:**
```
ImportError: No module named 'energy_tracker'
```

**Solution:**
```yaml
- name: Add Project to Python Path
  run: export PYTHONPATH=$PYTHONPATH:$(pwd)

- name: Run Tests
  run: python manage.py test
  env:
    PYTHONPATH: ${{ github.workspace }}
```

#### 2. **Database Migration Failures**

**Problem:**
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solution:**
```yaml
- name: Clean Migration State
  run: |
    rm -f db.sqlite3
    python manage.py migrate --run-syncdb
```

#### 3. **Static Files 404 Errors**

**Problem:**
```
Static files not found during tests
```

**Solution:**
```yaml
- name: Collect Static Files Before Tests
  run: python manage.py collectstatic --no-input

env:
  STATICFILES_STORAGE: 'django.contrib.staticfiles.storage.StaticFilesStorage'
```

#### 4. **Timezone Issues**

**Problem:**
```
Tests fail with timezone-related errors
```

**Solution:**
```yaml
env:
  TZ: 'America/New_York'  # Match production timezone
  USE_TZ: 'True'

- name: Verify Timezone
  run: python -c "import time; print(time.tzname)"
```

#### 5. **Secrets Not Available**

**Problem:**
```
KeyError: 'SECRET_KEY'
```

**Solution:**
```yaml
# For public repositories, use environment variables
env:
  SECRET_KEY: 'test-secret-key-for-ci-only'

# For private repositories, use secrets
env:
  SECRET_KEY: ${{ secrets.DJANGO_SECRET_KEY }}
```

#### 6. **Cache Issues**

**Problem:**
```
Old dependencies causing test failures
```

**Solution:**
```yaml
- name: Clear pip cache
  run: pip cache purge

- name: Install Fresh Dependencies
  run: pip install --no-cache-dir -r requirements.txt
```

#### 7. **Parallel Test Failures**

**Problem:**
```
Tests pass individually but fail when run in parallel
```

**Solution:**
```yaml
- name: Run Tests Sequentially
  run: python manage.py test --verbosity=2
  # Remove --parallel flag

# Or use test isolation
- name: Run with Test Isolation
  run: python manage.py test --parallel=1 --keepdb=false
```

---

## Best Practices Checklist

### Before Committing

- [ ] All tests pass locally
- [ ] Code is formatted and linted
- [ ] New tests added for new features
- [ ] Migration files are included
- [ ] requirements.txt is updated
- [ ] Sensitive data removed from code

### Workflow Configuration

- [ ] Using latest action versions (@v5, @v4, etc.)
- [ ] Caching enabled for dependencies
- [ ] Secrets properly configured
- [ ] Appropriate triggers set
- [ ] Permissions minimized
- [ ] Artifacts uploaded for failures
- [ ] Coverage reports generated

### Testing Strategy

- [ ] Fast tests run first (linting, syntax)
- [ ] Unit tests before integration tests
- [ ] Database migrations tested
- [ ] Static files collection verified
- [ ] Multiple Python versions tested
- [ ] Security scanning enabled
- [ ] Performance benchmarks (optional)

### Documentation

- [ ] Workflow files commented
- [ ] README updated with CI badge
- [ ] Contributing guide includes CI info
- [ ] Troubleshooting documented

---

## Additional Resources

### Official Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Django Testing Guide](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [Python Testing Best Practices](https://docs.python.org/3/library/unittest.html)

### Recommended Actions
- [actions/checkout@v4](https://github.com/actions/checkout)
- [actions/setup-python@v5](https://github.com/actions/setup-python)
- [actions/cache@v4](https://github.com/actions/cache)
- [actions/upload-artifact@v4](https://github.com/actions/upload-artifact)
- [codecov/codecov-action@v4](https://github.com/codecov/codecov-action)

### Tools & Libraries
- **Testing:** pytest, pytest-django, coverage, pytest-cov
- **Linting:** ruff, black, flake8, isort, pylint
- **Security:** safety, pip-audit, bandit
- **Performance:** pytest-benchmark, django-silk

---

## Energy Manager Specific Recommendations

### 1. **Activity Logging Tests**
```yaml
- name: Test Activity CRUD Operations
  run: python manage.py test energy_tracker.tests.test_activity_operations
```

### 2. **Dashboard Analytics Tests**
```yaml
- name: Test Dashboard Calculations
  run: python manage.py test energy_tracker.tests.test_dashboard
```

### 3. **Authentication Flow Tests**
```yaml
- name: Test User Authentication
  run: python manage.py test energy_tracker.tests.test_authentication
```

### 4. **Energy Level Validation**
```yaml
- name: Test Energy Scale (-2 to +2)
  run: python manage.py test energy_tracker.tests.test_models.EnergyLevelTests
```

### 5. **Timezone Handling Tests**
```yaml
- name: Test Activity Date Ordering
  run: python manage.py test energy_tracker.tests.test_ordering
  env:
    TZ: 'America/New_York'
```

---

## Conclusion

Implementing these best practices will ensure:
- ✅ Fast, reliable automated testing
- ✅ Early detection of bugs and regressions
- ✅ Consistent code quality
- ✅ Security vulnerability awareness
- ✅ Smooth deployment pipeline
- ✅ Team confidence in code changes

Start with a basic CI workflow and gradually add advanced features as your project grows. Remember: **working automation is better than perfect automation.**

---

**Last Updated:** November 2025  
**Application:** Energy Manager (Django 5.0)  
**Framework:** GitHub Actions
