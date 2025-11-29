# Contributing to Energy Manager

Thank you for your interest in contributing to Energy Manager! This document provides guidelines and instructions for contributing to the project.

## Development Workflow

### Setting Up Your Development Environment

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/Irine-Juliet/Energy-Manager.git
   cd Energy-Manager
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Configure Environment Variables**
   ```bash
   # Create a .env file in the project root
   echo "SECRET_KEY='your-secret-key-here'" > .env
   echo "DEBUG=True" >> .env
   ```

5. **Run Database Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```

### Running Tests Locally

#### Run All Tests
```bash
python manage.py test
```

#### Run Tests with Coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
# Open htmlcov/index.html in your browser
```

#### Run Specific Test Suite
```bash
# Run tests for a specific app
python manage.py test energy_tracker

# Run specific test class
python manage.py test energy_tracker.tests.ActivityModelTests

# Run specific test method
python manage.py test energy_tracker.tests.ActivityModelTests.test_activity_creation
```

#### Run Tests with Pytest
```bash
pytest
pytest --cov=. --cov-report=html
```

### Code Quality Checks

Before submitting a pull request, ensure your code passes all quality checks:

#### Format Code
```bash
# Auto-format with Black
black .

# Sort imports
isort .
```

#### Check Linting
```bash
# Run Ruff
ruff check .

# Run Flake8
flake8 .

# Check formatting (without changing files)
black --check .
isort --check-only .
```

#### Run All Quality Checks at Once
```bash
# Format
black .
isort .

# Then check
ruff check .
flake8 .
python manage.py check --deploy
```

### Continuous Integration

All pull requests must pass CI checks before merging. Our CI pipeline includes:

- ✅ **Code linting and formatting** (Ruff, Black, isort, Flake8)
- ✅ **Django system checks** (security, performance, configuration)
- ✅ **Database migrations** (ensuring migrations are valid and apply cleanly)
- ✅ **Unit and integration tests** (Python 3.10, 3.11, 3.12)
- ✅ **Code coverage reporting** (>80% target)
- ✅ **Security vulnerability scanning** (Safety, pip-audit)
- ✅ **Static file collection** (ensuring static assets build correctly)

View workflow status: [GitHub Actions](https://github.com/Irine-Juliet/Energy-Manager/actions)

### Branch Strategy

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/*`**: New features
- **`bugfix/*`**: Bug fixes
- **`hotfix/*`**: Urgent production fixes

### Making Changes

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, readable code
   - Follow Django best practices
   - Add tests for new functionality
   - Update documentation as needed

3. **Write Tests**
   - Add unit tests for models, forms, and utilities
   - Add integration tests for views and workflows
   - Ensure tests are isolated and repeatable
   - Aim for high code coverage (>80%)

4. **Run Tests and Quality Checks**
   ```bash
   # Run tests
   python manage.py test
   
   # Format code
   black .
   isort .
   
   # Check linting
   ruff check .
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: Add new feature description"
   ```

   **Commit Message Format:**
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting)
   - `refactor:` Code refactoring
   - `test:` Adding or updating tests
   - `chore:` Maintenance tasks

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to GitHub and create a pull request
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure CI checks pass

### Pull Request Guidelines

- **Title**: Clear and descriptive (e.g., "Add energy level filtering to dashboard")
- **Description**: Explain what changes were made and why
- **Tests**: Include tests for new features or bug fixes
- **Documentation**: Update README, docstrings, or comments as needed
- **Breaking Changes**: Clearly indicate any breaking changes
- **Screenshots**: Include screenshots for UI changes

### Code Style Guidelines

#### Python
- Follow PEP 8 style guide
- Use Black for formatting (line length: 88)
- Use meaningful variable and function names
- Add docstrings to classes and complex functions
- Keep functions small and focused

#### Django
- Follow Django coding style
- Use Django ORM instead of raw SQL
- Use Django forms for validation
- Follow Django's security best practices
- Use timezone-aware datetime objects

#### Templates
- Use Django template language idiomatically
- Keep logic minimal in templates
- Use template inheritance appropriately
- Include CSRF tokens in forms

#### JavaScript
- Use modern ES6+ syntax
- Keep JavaScript minimal (progressive enhancement)
- Add comments for complex logic

### Testing Guidelines

#### Test Organization
```
energy_tracker/
├── tests/
│   ├── __init__.py
│   ├── test_models.py      # Model tests
│   ├── test_views.py       # View tests
│   ├── test_forms.py       # Form tests
│   ├── test_utils.py       # Utility function tests
│   └── test_integration.py # Integration tests
```

#### Writing Good Tests
- Test one thing per test method
- Use descriptive test names
- Use Django's test client for integration tests
- Mock external dependencies
- Use fixtures or factories for test data
- Clean up after tests (Django does this automatically)

#### Test Naming Convention
```python
def test_<what_is_being_tested>_<expected_outcome>(self):
    # Example:
    def test_activity_creation_with_valid_data_succeeds(self):
        # Test code
```

### Database Migrations

#### Creating Migrations
```bash
# Create migrations for model changes
python manage.py makemigrations

# Create empty migration for data migrations
python manage.py makemigrations --empty energy_tracker
```

#### Applying Migrations
```bash
# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

#### Migration Best Practices
- Always create migrations for model changes
- Review generated migrations before committing
- Use data migrations for schema changes that require data transformation
- Test migrations in a local database before committing
- Include both forward and reverse migrations

### Security Considerations

- Never commit sensitive data (passwords, API keys, SECRET_KEY)
- Use environment variables for configuration
- Validate all user input
- Use Django's built-in security features (CSRF, XSS protection)
- Keep dependencies up to date
- Run security scans (`safety check`, `pip-audit`)

### Getting Help

- **Issues**: Check existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Refer to Django documentation and project docs

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project

## Thank You!

Your contributions make Energy Manager better for everyone. We appreciate your time and effort!
