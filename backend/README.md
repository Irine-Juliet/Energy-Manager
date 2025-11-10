# Energy Manager - Backend (Django REST API)

## Setup

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r ../requirements.txt
```

3. Create `.env` file in project root:
```bash
cp ../.env.example ../.env
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Start development server:
```bash
python manage.py runserver
```

The backend API will run on `http://localhost:8000`

## Tech Stack

- **Django 5.0** - Web framework
- **Django REST Framework** - API framework
- **Simple JWT** - Token authentication
- **Django CORS Headers** - CORS handling
- **SQLite** - Database (development)
