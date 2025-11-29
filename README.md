# Energy Manager

A personal energy tracker to help you identify draining and energizing activities.

## Tech Stack

- **Django 5.0** - Web framework
- **Tailwind CSS** - Styling 
- **Chart.js** - Data visualization
- **SQLite** - Database

## Project Structure

```
Energy-Manager/
├── energy_manager/          # Django project configuration
│   ├── settings.py         # Project settings
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI config
├── energy_tracker/         # Main app (your features live here)
│   ├── models.py          # Activity model
│   ├── views.py           # View functions
│   ├── forms.py           # Django forms
│   ├── urls.py            # App URL routing
│   └── admin.py           # Admin configuration
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   └── energy_tracker/   # App templates
├── venv/                 # Virtual environment
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## Setup

1. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create `.env` file:**
```bash
cp .env.example .env
# Edit .env with your SECRET_KEY
```

4. **Run migrations:**
```bash
python manage.py migrate
```

5. **Create superuser:**
```bash
python manage.py createsuperuser
```

6. **Start development server:**
```bash
python manage.py runserver
```

7. **Open in browser:**
```
http://localhost:8000
```

## Core Features

- ✅ User authentication (signup/login)
- ✅ Activity logging with energy ratings (-2 to +2)
- ✅ Daily summary dashboard
- ✅ Weekly energy trend visualization
- ✅ Activity history with pagination
- ✅ Edit/delete activities

## Activity Ordering and Display Logic

All activity lists are ordered by `activity_date` (when the activity occurred), not by `created_at` (when it was logged). This allows users to:

- Log activities retrospectively (e.g., log breakfast at noon)
- Maintain chronological accuracy
- See activities in the order they actually happened

### Homepage Display Rules

The homepage shows **up to 5 most recent activities** from today:
- Sorted by `activity_date` descending (most recent first)
- Limited to 5 items to keep the homepage clean and focused
- If you have more than 5 activities today, only the 5 most recent appear
- To see all activities, visit the Activity History page

**Example:** If you log "Breakfast at 8 AM" at 2 PM, and you already have 5 activities that occurred after 8 AM, breakfast will NOT appear on the homepage (because it's not in the top 5 most recent). However, it will appear in the Activity History page.

### Activity History Page

The Activity History page shows ALL activities within the selected time window (day/week/month), ordered chronologically by when they occurred. Use this page to:
- View complete activity history
- Search and filter activities
- Review activities that don't appear in the homepage's top 5
