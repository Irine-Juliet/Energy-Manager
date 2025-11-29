# Energy Manager - Application Descriptor

## Overview

Energy Manager is a personal energy tracking web application designed to help users identify activities that drain or energize them throughout the day. Users can log activities with associated energy levels, view analytics on their energy patterns, and gain insights into their daily productivity and well-being.

## Application Purpose

The application enables users to:
- **Log daily activities** with timestamps, duration, and energy impact ratings
- **Track energy levels** throughout the day using a -2 to +2 scale
- **Visualize patterns** through interactive charts and dashboards
- **Identify trends** to understand which activities are draining or energizing
- **Make informed decisions** about time management and activity planning
- **Review history** with filtering and search capabilities

## Application Classification

### Primary Type
**Server-Side Rendered Multi-Page Application (SSR MPA)**

### Rendering Model
- **Server-Side Rendering (SSR)** - Django templates generate complete HTML pages on the server
- **Progressive Enhancement** - Core functionality works without JavaScript, enhanced with client-side features
- **Selective AJAX** - Used for specific interactions (activity logging, autocomplete) without full page reloads

### Architecture Pattern
**3-Tier Web Application**

1. **Presentation Layer**
   - HTML templates with Django Template Language
   - Tailwind CSS for responsive styling
   - Chart.js for data visualization

2. **Application Layer**
   - Django 5.0 web framework
   - Python-based business logic
   - View functions handling HTTP requests/responses
   - Form validation and processing

3. **Data Layer**
   - SQLite relational database
   - Django ORM for data access
   - User authentication and session management

### Application Category
- **CRUD Application** - Full Create, Read, Update, Delete operations on activity data
- **Data-Driven Dashboard** - Analytics and insights from user activity logs
- **Authenticated Web App** - User-specific data with login/signup functionality
- **Traditional Dynamic Web Application** - Server-generated pages with database-backed content

### Key Characteristics
- **Multi-Page Architecture** - Distinct pages with full page reloads for navigation
- **Session-Based Authentication** - Server-side session management with Django auth
- **Responsive Design** - Mobile-friendly interface using Tailwind CSS
- **Real-time Visualizations** - Client-side charts updated with server data
- **RESTful Patterns** - Clean URL structure and HTTP method conventions

## Technical Architecture

### Tech Stack

#### Backend
- **Framework**: Django 5.0
- **Language**: Python 3.x
- **Database**: SQLite (with PostgreSQL support via dj-database-url)
- **ORM**: Django ORM
- **Authentication**: Django's built-in auth system
- **Configuration**: python-decouple for environment variables

#### Frontend
- **Templating**: Django Template Language
- **CSS Framework**: Tailwind CSS
- **JavaScript Library**: Chart.js for visualizations
- **Enhancement**: Vanilla JavaScript for AJAX interactions
- **Icons/UI**: Custom CSS with Tailwind utilities

#### Infrastructure
- **Web Server**: Gunicorn (production)
- **Static Files**: WhiteNoise for efficient static file serving
- **Deployment**: Render.yaml configuration for cloud deployment

### Project Structure

```
Energy-Manager/
├── energy_manager/          # Django project configuration
│   ├── settings.py         # Application settings & middleware
│   ├── urls.py            # Root URL routing
│   ├── wsgi.py            # WSGI deployment interface
│   └── asgi.py            # ASGI interface (async support)
│
├── energy_tracker/         # Main application module
│   ├── models.py          # Data models (Activity, UserProfile)
│   ├── views.py           # View functions (business logic)
│   ├── forms.py           # Form definitions and validation
│   ├── urls.py            # App-specific URL patterns
│   ├── utils.py           # Helper functions
│   ├── admin.py           # Django admin configuration
│   └── migrations/        # Database schema migrations
│
├── templates/             # HTML templates
│   ├── base.html         # Base template with common layout
│   └── energy_tracker/   # App-specific templates
│       ├── homepage.html
│       ├── dashboard.html
│       ├── log_activity.html
│       ├── activity_history.html
│       ├── login.html
│       ├── signup.html
│       └── settings.html
│
├── db.sqlite3            # SQLite database file
├── manage.py            # Django management CLI
├── requirements.txt     # Python dependencies
└── render.yaml         # Deployment configuration
```

## Core Features

### 1. User Authentication
- **Signup**: New user registration with username/email/password
- **Login**: Secure authentication with session management
- **Logout**: Session termination
- **Password Management**: Change password functionality
- **User Profiles**: Customizable settings (theme preferences, notifications)

### 2. Activity Logging
- **Quick Logging**: Add activities with name, duration, and energy level
- **Retrospective Logging**: Log past activities with custom timestamps
- **Energy Scale**: -2 (very draining) to +2 (very energizing)
- **Duration Tracking**: Record how long activities last
- **Auto-complete**: Smart suggestions based on frequently logged activities
- **AJAX Submission**: Log activities without page reload

### 3. Dashboard & Analytics
- **Today's Overview**: Current day's average energy level and activity count
- **Timeline Visualization**: Activities plotted throughout the day
- **Hourly Averages**: Energy levels averaged per hour (24-hour view)
- **Time Distribution**: Hours spent in each energy category
- **Weekly Trends**: 7-day average energy chart
- **Top Activities**: Most draining and energizing activities identified

### 4. Activity History
- **Comprehensive Listing**: All logged activities with pagination
- **Multiple Views**: Day/week/month time windows
- **Search**: Filter by activity name
- **Energy Filtering**: View only specific energy levels
- **Edit & Delete**: Modify or remove logged activities
- **Bulk Operations**: Delete multiple activities at once
- **Chronological Ordering**: Activities sorted by occurrence time

### 5. Settings & Personalization
- **Theme Selection**: Light/dark mode preferences
- **Notification Settings**: Control alert preferences
- **Account Management**: View profile information
- **Password Changes**: Update security credentials

## Data Model

### Activity Model
```python
- id: Primary key (auto-generated)
- user: Foreign key to Django User
- name: Activity name (string)
- activity_date: When activity occurred (datetime)
- energy_level: Energy rating (integer: -2 to +2)
- duration: Activity length in minutes (integer)
- created_at: Record creation timestamp
```

### UserProfile Model
```python
- id: Primary key (auto-generated)
- user: One-to-one with Django User
- theme: UI theme preference (light/dark)
- notifications_enabled: Boolean flag
```

## Request-Response Flow

### Typical Page Request Flow

1. **User Action**: Browser requests URL (e.g., `/dashboard/`)
2. **URL Routing**: Django URLs match pattern to view function
3. **Authentication Check**: `@login_required` decorator validates session
4. **View Processing**:
   - Query database via Django ORM
   - Calculate aggregations (averages, counts)
   - Process form data (if POST request)
5. **Template Rendering**: 
   - Context data passed to template
   - Django template engine generates HTML
6. **Response**: Complete HTML page sent to browser
7. **Client Rendering**: Browser displays page and loads static assets (CSS, JS)

### AJAX Request Flow (e.g., Log Activity)

1. **User Interaction**: Fill form and click submit
2. **JavaScript Intercept**: Prevent default form submission
3. **AJAX Request**: Send JSON data to server via XMLHttpRequest
4. **Server Processing**: View function processes data, saves to database
5. **JSON Response**: Server returns success/error JSON
6. **Client Update**: JavaScript updates UI without page reload

## Design Philosophy

### Activity Ordering Logic
All activity lists prioritize **occurrence time** (`activity_date`) over **creation time** (`created_at`):
- **Rationale**: Users often log activities retrospectively
- **Benefit**: Maintains chronological accuracy
- **Example**: Breakfast logged at 2 PM appears at 8 AM slot

### Homepage Display Rules
- Shows **top 5 most recent activities** from today only
- Filtered by `activity_date` within current day
- Sorted descending (most recent first)
- Provides quick overview without overwhelming users
- Full history accessible via Activity History page

### Energy Scale
- **-2**: Very draining (exhausting, depleting)
- **-1**: Somewhat draining (tiring, low energy)
- **0**: Neutral (no significant impact)
- **+1**: Somewhat energizing (refreshing, positive)
- **+2**: Very energizing (invigorating, highly positive)

## Security Features

### Authentication & Authorization
- Session-based authentication with Django middleware
- Password hashing with Django's built-in validators
- CSRF protection on all forms
- Login required decorators on protected views
- User-scoped queries (users only see their own data)

### Data Protection
- SQL injection prevention via ORM parameterized queries
- XSS protection through template auto-escaping
- Secure password validation rules
- HTTPS enforcement in production (via middleware)

### Configuration Security
- Environment variables for sensitive data (SECRET_KEY)
- Debug mode disabled in production
- Allowed hosts whitelist
- Database connection pooling for efficiency

## Deployment Architecture

### Production Environment
- **Platform**: Render (Platform-as-a-Service)
- **Web Server**: Gunicorn WSGI server
- **Static Files**: WhiteNoise middleware
- **Database**: SQLite (upgradeable to PostgreSQL)
- **Environment**: Configured via `.env` file

### Key Settings
- **Time Zone**: America/New_York
- **Static Files**: Compressed and cached
- **Session Engine**: Database-backed sessions
- **Login URLs**: Configured redirects for auth flow

## Development Workflow

### Setup Process
1. Create virtual environment
2. Install dependencies from `requirements.txt`
3. Configure `.env` with SECRET_KEY
4. Run database migrations
5. Create superuser
6. Start development server

### Database Migrations
- Automatic schema versioning
- Incremental migration files in `migrations/`
- Data migrations for schema changes (e.g., energy scale updates)

## Performance Considerations

### Database Optimization
- Indexed fields on user_id for faster queries
- Aggregate queries for dashboard statistics
- Pagination on activity history (20 per page)
- Limited querysets for homepage (top 5)

### Static Asset Handling
- Compressed CSS/JS in production
- Manifest-based static files with WhiteNoise
- Browser caching headers
- CDN-ready static file serving

### Query Efficiency
- Selective field retrieval with `.values()`
- Annotated queries for aggregations
- Single queries vs. multiple lookups
- Timezone-aware datetime filtering

## Future Enhancement Opportunities

### Potential Features
- **Data Export**: CSV/JSON download of activity history
- **Goals & Targets**: Set energy level objectives
- **Insights & Recommendations**: AI-powered activity suggestions
- **Social Features**: Share insights or compare anonymously
- **Mobile App**: Native iOS/Android applications
- **API**: RESTful API for third-party integrations
- **Advanced Analytics**: Correlation analysis, predictive modeling

### Technical Improvements
- **Migration to SPA**: React/Vue frontend for smoother UX
- **Real-time Updates**: WebSocket support for live dashboard
- **Caching Layer**: Redis for session and query caching
- **Search Engine**: Full-text search with Elasticsearch
- **Testing**: Comprehensive unit and integration tests
- **CI/CD Pipeline**: Automated testing and deployment

## Summary

Energy Manager is a robust, user-focused web application that combines Django's powerful backend capabilities with modern frontend libraries to deliver an intuitive energy tracking experience. Its server-side rendered architecture ensures reliability and simplicity, while selective client-side enhancements provide a smooth user experience. The application follows web development best practices, prioritizes security, and maintains a clean separation of concerns across its three-tier architecture.

**Classification**: Server-Side Rendered Multi-Page Application (SSR MPA)  
**Pattern**: 3-Tier Web Architecture  
**Category**: CRUD Dashboard Application with Analytics  
**Framework**: Django 5.0 (Python)  
**Frontend**: Django Templates + Tailwind CSS + Chart.js  
**Database**: SQLite (production-ready for PostgreSQL)
