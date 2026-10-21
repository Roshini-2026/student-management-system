# Task 15: Dashboard and Reports
- Admin-only dashboard (view_reports permission) showing total students, active courses, instructors, students per status and per course.
- Recently registered students and recent enrollment activity (the latest changed records) are shown in tables, and a Chart.js bar chart shows students per course.
- Filters: course and enrollment date range. Invalid filter values are ignored and the error is shown.
- All figures use database queries (Count, group by), and the number of queries stays the same as data grows.
- Empty data shows a message. Tests cover access, totals, filters, empty data and query count.
- Errors and fixes: none.