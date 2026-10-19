# Task 7: Student CRUD
- Built pages to register, list, view, edit and delete students.
- StudentForm is a ModelForm, so the model's rules (required fields, unique email) are reused.
- After saving, the view redirects, so refreshing doesn't resubmit the form.
- Delete shows a confirmation page first, and only a POST deletes.
- Wrong student IDs give a 404, and pages need login for now (Task 9 adds real login).
- Phone numbers must be exactly 10 digits, with +91 shown as a fixed prefix.
- Errors and fixes: a test used a valid 10-digit number as "invalid", so I changed it to an 11-digit one.