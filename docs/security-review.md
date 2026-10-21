# Security Review

| Area | Check | Result |
|---|---|---|
| Secrets | SECRET_KEY, DEBUG, ALLOWED_HOSTS, email and SMTP credentials come from .env. .env is in .gitignore. | Pass |
| Secrets | Searched Git history for secret keys and for .env | Pass (see Task 19 commands) |
| Configuration | DEBUG is False and secure cookies, HTTPS redirect and HSTS are on in production | Pass |
| Deployment check | python manage.py check --deploy | See docs/deployment-check.txt |
| Authentication | Passwords hashed by Django and never stored as plain text; strength rules on; login errors don't reveal whether the username exists; logout is POST only | Pass (accounts/tests.py) |
| Sessions | HTTP-only cookies, 8 hour lifetime, session ends on logout | Pass (core/test_security.py) |
| Authorization | Permissions are checked on the server (403) for the website, admin and API; hidden buttons are only cosmetic | Pass (core/test_roles.py, test_catalog.py, api/tests.py) |
| Restricted data | Viewers can't see mobile number, date of birth, address or documents, in pages or the API. No URL contains a user id: the profile page always shows the logged-in user. | Pass |
| CSRF | Every form has a token, POSTs without a token get 403, and the API uses tokens | Pass (core/test_security.py) |
| Input validation | Server-side validation in forms and serializers; database unique and range constraints | Pass |
| Uploads | Extension, real content and size are checked; random server-side filenames; documents live outside the public media folder and are served only after a permission check | Pass (core/test_files.py) |
| SQL injection | Only ORM queries and validated filter values; no raw SQL | Pass (grep check) |
| XSS | Django auto-escapes templates; the only |safe is Django's own password help text | Pass |
| Error handling | Production shows plain 404, 403 and 500 pages with no traceback | Pass (core/test_security.py) |
| Logging | Only the student id is logged for emails; no passwords or tokens | Pass |
| Dependencies | pip-audit run on requirements.txt | [paste: no known vulnerabilities, or what you upgraded] |
| Code quality | ruff removed unused imports; code is organised into models, forms, views, templates, services (emails, files) and tests | Pass |

## Issues found and fixed
- Weak "django-insecure" key replaced with a generated key.
- Hard-coded ALLOWED_HOSTS moved to .env.
- Bulk delete left uploaded files on disk (fixed with a signal).
- Course lists were unordered under Count (explicit ordering added).

## Remaining limitations
See docs/known-issues.md: no login rate limiting, local file storage, static files need WhiteNoise or a web server in production.