# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the Energy Manager application.

## Overview

The Energy Manager project uses GitHub Actions for continuous integration and deployment, ensuring code quality, security, and reliability with every change.

## Workflows

### `ci.yml` - Main CI Pipeline

**Triggers:**
- Push to `main`, `develop`, feature branches, bugfix branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Jobs:**

1. **Lint** - Code Quality & Linting
   - Runs Ruff for Python linting
   - Checks code formatting with Black
   - Validates import sorting with isort
   - Runs Flake8 for additional checks

2. **Security** - Vulnerability Scanning
   - Checks dependencies with Safety
   - Audits packages with pip-audit
   - Generates security report (uploaded as artifact)

3. **Django Checks** - System Validation
   - Runs Django system checks with deployment settings
   - Validates migrations are up to date
   - Ensures no pending migrations

4. **Migrations** - Database Testing
   - Applies all migrations to clean database
   - Creates test superuser
   - Validates migration integrity

5. **Test** - Unit & Integration Tests
   - Matrix testing across Python 3.10, 3.11, 3.12
   - Runs full test suite with parallel execution
   - Generates code coverage reports
   - Uploads coverage artifacts (HTML and XML)
   - Uploads test database on failure for debugging

6. **Static Files** - Asset Collection
   - Collects static files with WhiteNoise
   - Validates static asset configuration
   - Uploads static files as artifact

7. **Summary** - CI Results
   - Aggregates all job statuses
   - Creates workflow summary
   - Fails if required jobs fail

**Environment Variables:**
- `PYTHON_VERSION`: 3.12 (default for non-matrix jobs)
- `SECRET_KEY`: Test key for CI (not for production)
- `DEBUG`: False
- `ALLOWED_HOSTS`: localhost,127.0.0.1
- `TZ`: America/New_York

## Artifacts

Workflows generate artifacts that are retained for debugging and analysis:

| Artifact | Retention | Description |
|----------|-----------|-------------|
| `security-report` | 90 days | Security vulnerability scan results |
| `coverage-report-{version}` | 30 days | HTML coverage report per Python version |
| `coverage-xml` | 30 days | XML coverage report (Python 3.12 only) |
| `test-database-{version}` | 7 days | Test database on failure for debugging |
| `static-files` | 7 days | Collected static assets |

## Status Checks

The following checks must pass before merging pull requests:

- ✅ Lint - Code quality and formatting
- ✅ Django Checks - System validation
- ✅ Migrations - Database migration testing
- ✅ Test (all Python versions) - Full test suite

Security and static file checks run but don't block merges (continue-on-error).

## Local Testing

To test CI workflows locally before pushing:

### Run Tests Locally
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run linting
ruff check .
black --check .
isort --check-only .
flake8 .

# Run Django checks
python manage.py check --deploy
python manage.py makemigrations --check --dry-run --no-input

# Run tests with coverage
coverage run --source='.' manage.py test --verbosity=2
coverage report
```

### Simulate CI Environment
```bash
export SECRET_KEY='test-secret-key'
export TZ='America/New_York'
export DEBUG='False'

python manage.py migrate --no-input
python manage.py test --verbosity=2 --parallel=auto
python manage.py collectstatic --no-input --clear
```

## Troubleshooting

### Common Issues

#### Tests Fail in CI but Pass Locally

**Possible causes:**
- Python version mismatch
- Timezone configuration difference
- Missing environment variables

**Solutions:**
```bash
# Test with same Python version as CI
python3.12 manage.py test

# Set timezone
export TZ='America/New_York'
python manage.py test

# Use fresh database
rm db.sqlite3
python manage.py migrate
python manage.py test
```

#### Linting Failures

**Fix automatically:**
```bash
black .
isort .
ruff check . --fix
```

#### Migration Issues

**Check migration status:**
```bash
python manage.py makemigrations --check --dry-run
python manage.py showmigrations
```

#### Coverage Too Low

**View coverage report:**
```bash
coverage run --source='.' manage.py test
coverage report --show-missing
coverage html
open htmlcov/index.html
```

### Viewing Workflow Logs

1. Go to [GitHub Actions](https://github.com/Irine-Juliet/Energy-Manager/actions)
2. Click on the workflow run
3. Click on individual jobs to see logs
4. Download artifacts for detailed reports

### Re-running Failed Workflows

1. Navigate to the failed workflow run
2. Click "Re-run jobs" → "Re-run failed jobs"
3. Or "Re-run all jobs" for complete re-run

## Maintenance

### Updating Action Versions

Current action versions:
- `actions/checkout@v4`
- `actions/setup-python@v5`
- `actions/cache@v4`
- `actions/upload-artifact@v4`

Check for updates periodically and update workflow files.

### Updating Python Versions

To add or remove Python versions from the test matrix:

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']  # Modify this list
```

### Updating Dependencies

Regularly update test dependencies in `requirements-dev.txt`:

```bash
pip list --outdated
# Update versions in requirements-dev.txt
```

## Best Practices

1. **Always run tests locally before pushing**
2. **Fix linting issues immediately** - don't let them accumulate
3. **Review security scan results** - address vulnerabilities promptly
4. **Monitor code coverage** - aim for >80%
5. **Keep dependencies updated** - check monthly for updates
6. **Test migrations** - verify migrations work before committing
7. **Write meaningful commit messages** - helps with debugging CI failures

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Django Testing Guide](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines
- [README.md](../README.md) - Project documentation

---

**Last Updated:** November 29, 2025  
**Maintained by:** Energy Manager Development Team
