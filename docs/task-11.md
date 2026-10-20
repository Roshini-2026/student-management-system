# Task 11: Course and Instructor Models
- Added Instructor and Course models. A course can have many instructors, and an instructor can teach many courses.
- A student now links to one course. Courses with students can't be deleted (PROTECT).
- Built pages to manage courses and instructors, with student counts and a course details page.
- Used select_related and prefetch_related so lists don't run a query per row.
- Errors and fixes: deleted old test students before changing the course field to a relationship.