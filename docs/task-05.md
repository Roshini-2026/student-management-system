# Task 5: Contact Form
- Built the form in forms.py, with name, email, subject and message required.
- Django checks the email and phone on the server, so turning off JavaScript doesn't skip the checks.
- Errors show under each field, typed values stay, and a success message appears after sending.
- The form has a CSRF token, and I wrote tests for valid and invalid submissions.
- Errors and fixes: the browser stopped my invalid test, so I turned off JavaScript in DevTools to test Django's checks.