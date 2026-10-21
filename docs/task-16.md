# Task 16: REST API
- Built an api app with Django REST Framework: students and courses endpoints for list, detail, create, update (PUT and PATCH) and delete.
- Token login at /api/token/. Permissions reuse the website roles (Admin, Staff, Viewer), and Viewers don't see private student details.
- Supports pagination, search, filters and ordering. Validation errors, wrong IDs and bad JSON return clear JSON with the right status codes. Deleting a course that has students returns 409.
- Endpoints are documented in docs/api.md and covered by automated tests. I also tested them in the browser (DRF browsable API), and the results are in docs/api-test-results.md.
- Errors and fixes: moved the pagination class to api/pagination.py to fix a circular import, and fixed the make_student test helper.