# Task 8: Search, Filters, Sorting and Pagination
- Added a filter form that searches name and email and filters by course and gender.
- Sorting only works on a fixed list of fields, so strange values in the URL are ignored.
- The list is split into pages (10, 25 or 50) and the filters stay when changing pages.
- Everything runs as database queries, so Python never loads all students.
- Errors and fixes: used paginator.ELLIPSIS (not ellipsis), and made the course list load when the form is validated.