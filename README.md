# Student Management System

A Django web application for managing students, courses and instructors.
Built as a practical learning project.

## Requirements

- Python 3.x (check with `python --version`)
- Git

## Setup

1. Clone the repository
```
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
```

2. Create a virtual environment
```
   python -m venv venv
```

3. Activate it
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. Install dependencies
```
   pip install -r requirements.txt
```

5. Create your environment file
   - Copy `.env.example` to `.env`
   - Set your own values inside `.env`

6. Apply database migrations
```
   python manage.py migrate
```

## Run the project

```
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Project structure

- `manage.py` - command-line tool for the project
- `web_practice/` - project settings and main URL configuration
- `core/` - the main application
- `requirements.txt` - Python dependencies
- `docs/` - task notes and screenshots

## Status

Task 1 (project setup) complete. More features are being added task by task.