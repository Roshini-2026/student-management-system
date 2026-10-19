# Task 6: Student Model and Django Admin

## Fields
- id: the Student ID, Django adds it automatically.
- full_name: the student's name, required.
- email: must be unique, so no two students share one.
- mobile_number: stored as text so a + or leading zero is kept.
- gender: Male, Female or Other.
- date_of_birth: optional.
- course: course name as text for now (changes in Task 11).
- address: optional.
- is_active: shows whether the student is active.
- created_at: set once when the record is created.
- updated_at: changes every time the record is saved.

## Concepts
- Model: a Python class that becomes a database table.
- Migration: a file that tells Django how to change the database.
- ORM: lets me use Python instead of SQL to work with data.
- Primary key: a unique id for each row.
- Unique constraint: the database refuses duplicate values.
- null vs blank: null is for the database, blank is for forms.

## Testing
- Added and edited students in Admin.
- Duplicate email and empty required fields were rejected.
- Data stayed after restarting the server.
- python manage.py test passes.

## Errors and fixes
- None.