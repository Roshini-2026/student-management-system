# Task 14: Email Notifications
- When a student is created, an enrollment confirmation email is sent after the database save is committed.
- The email service is core/emails.py, with HTML and text templates in templates/emails/. A signal triggers it, so the web page, Admin and the future API all send it.
- Failures are caught and logged (student id only), so a mail problem never undoes an enrollment.
- Settings come from .env. In development emails print in the terminal.
- To test a real SMTP provider: in .env set EMAIL_MODE=smtp, EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER and EMAIL_HOST_PASSWORD (for example a Mailtrap inbox, or Gmail with an app password), restart the server and register a student. Never commit .env. Set EMAIL_MODE back to console afterwards.
- Errors and fixes: removed the old EMAIL_BACKEND setting because Django 6.1 uses MAILERS.