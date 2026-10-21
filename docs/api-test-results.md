# API Test Results

Tested in the browser (Django REST Framework browsable API), logged in as Admin, Staff, Viewer and as an anonymous user.

| # | Request | Role | Expected | Actual |
|---|---|---|---|---|
| 1 | GET /api/students/ | Admin | 200 | |
| 2 | GET /api/students/?search=ravi&page_size=5 | Admin | 200 | |
| 3 | GET /api/students/<id>/ | Admin | 200 | |
| 4 | GET /api/students/9999/ | Admin | 404 | |
| 5 | POST /api/students/ (valid) | Admin | 201 | |
| 6 | POST /api/students/ ({}) | Admin | 400 | |
| 7 | POST /api/students/ (duplicate email) | Admin | 400 | |
| 8 | PUT /api/students/<id>/ | Admin | 200 | |
| 9 | GET /api/courses/ | Admin | 200 | |
| 10 | POST /api/courses/ (valid) | Admin | 201 | |
| 11 | DELETE /api/courses/<id>/ (has students) | Admin | 409 | |
| 12 | DELETE /api/students/<id>/ | Admin | 204 | |
| 13 | GET /api/students/ (not logged in) | None | 401 | |
| 14 | GET /api/students/ | Viewer | 200 (no private fields) | |
| 15 | GET /api/courses/ | Viewer | 403 | |
| 16 | GET /api/students/ | Staff | 200 | |

Create, edit and delete restrictions for Staff and Viewer (403) are verified by the automated tests in api/tests.py.
Run python manage.py test: all tests pass.