# Setting Up Automatic Tests for Pull Requests

To ensure code quality and prevent regressions, it's best practice to run automated tests whenever a new Pull Request (PR) is opened. This guide explains how to set up automatic test runs using GitHub Actions for your Django project.

## Prerequisites
- Your code is hosted on GitHub.
- You have a test suite (e.g., Django tests in `energy_tracker/tests.py`).

## Step 1: Create a GitHub Actions Workflow
1. In your project root, create a directory called `.github/workflows` if it doesn't exist.
2. Inside this directory, create a file named `ci.yml` (or any name you prefer).

## Step 2: Add Workflow Configuration
Paste the following example into `.github/workflows/ci.yml`:

```yaml
name: Django CI

on:
  pull_request:
    branches:
      - main
      - feature/*

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run migrations
        run: |
          python manage.py migrate
      - name: Run tests
        run: |
          python manage.py test
```

## Step 3: Commit and Push
- Add, commit, and push the `.github/workflows/ci.yml` file to your repository.
- Now, whenever a new PR is opened, GitHub Actions will automatically run your test suite and report results in the PR.

## Customization
- You can adjust the workflow to use SQLite (default for Django) by removing the `services` section.
- For more advanced setups, add steps for linting, coverage, or other checks.

## Resources
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Django Testing Documentation](https://docs.djangoproject.com/en/5.0/topics/testing/)

---

**Tip:** Make sure your tests are reliable and do not depend on local files or environment variables not set in the workflow.
