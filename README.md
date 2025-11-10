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
