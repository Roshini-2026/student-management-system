- **manage.py**: command-line tool to run and manage the project (runserver, migrate, startapp).

## Concepts
- Python: a general-purpose programming language.
- Django: a Python web framework that provides the URLs, database, forms, authentication and admin.
- Project: the whole website and its settings (web_practice). App: one feature inside it (core, accounts, api).
- Virtual environment: keeps this project's packages separate from other projects.
- settings.py holds configuration. urls.py maps web addresses to views.


- **views.py**: receives a request, processes data, and returns a response (HTML page or JSON).

- **models.py**: Python classes that Django turns into database tables.

- **asgi.py**: entry point for asynchronous web servers (for example WebSockets).

- **wsgi.py**: entry point for traditional synchronous web servers, used when deploying.