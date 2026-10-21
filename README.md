# Student Management System

A Django web application for managing students, courses and instructors, with role-based access, file uploads, email notifications, a dashboard and a REST API.

## Features
- Registration, login, logout, profile, password change and reset
- Roles: Admin (everything), Staff (view, add and edit students, view courses), Viewer (view students only)
- Student CRUD with validation, search, course and gender filters, sorting and pagination
- Courses and instructors with student counts and a course details page
- Profile photos and private supporting documents with validation
- Enrollment confirmation emails (console in development, SMTP optional)
- Admin-only dashboard with statistics, filters and a chart
- Token-protected REST API for students and courses
- Customised Django Admin, responsive Bootstrap interface
- Automated tests, security review and deployment check

## Requirements
Python 3.13 and Git.

## Setup
```
git clone https://github.com/<your-username>/<repo>.git
cd <repo>
python -m venv venv
source venv/Scripts/activate      # Windows (Git Bash). Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # then edit the values (see below)
python manage.py migrate
python manage.py setup_roles
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/. Give users a role in /admin/ (Users, then Groups: Admin, Staff or Viewer). New registrations start as Viewers.

## Environment variables (.env)
| Variable | Purpose |
|---|---|
| SECRET_KEY | Django secret key. Generate a new one for every environment. |
| DEBUG | True for development, False for production |
| ALLOWED_HOSTS | Comma-separated host names |
| EMAIL_MODE | `console` (prints emails in the terminal) or `smtp` |
| SENDER_NAME, SENDER_ADDRESS | Name and address shown as the email sender |
| EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD | Needed only when EMAIL_MODE=smtp. For Gmail, use an app password. |

Never commit `.env`.

## Tests
```
python manage.py test
```

## API
See [docs/api.md](docs/api.md). Get a token at `POST /api/token/` and send `Authorization: Token <token>`.

## Documentation
- [Architecture and code decisions](docs/architecture.md)
- [Database diagram](docs/database-diagram.md)
- [API documentation](docs/api.md) and [API test results](docs/api-test-results.md)
- [Test results](docs/test-results.txt) and [coverage](docs/coverage.txt)
- [Security review](docs/security-review.md) and [deployment check](docs/deployment-check.txt)
- [Known issues](docs/known-issues.md)
- Task notes: docs/task-01.md to docs/task-20.md

## Project structure
- `web_practice/` project settings and URLs
- `core/` students, courses, instructors, dashboard, emails, file handling
- `accounts/` registration, login, passwords, roles command
- `api/` REST API
- `templates/`, `static/` HTML, CSS and JavaScript