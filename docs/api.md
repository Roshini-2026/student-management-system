# Student Management API

Base URL: http://127.0.0.1:8000/api/    All requests and responses use JSON.

## Authentication
POST /api/token/   body: {"username": "...", "password": "..."}   ->  {"token": "abc123"}
Send the token with every other request:  Authorization: Token abc123
No token: 401. Wrong role: 403.

## Roles
| Role   | Students                  | Courses            |
|--------|---------------------------|--------------------|
| Admin  | list, view, add, edit, delete | all            |
| Staff  | list, view, add, edit     | list and view only |
| Viewer | list and view (no mobile number, date of birth, address) | no access |

## Endpoints
| Method | URL | What it does | Success |
|---|---|---|---|
| GET | /api/students/ | List students | 200 |
| POST | /api/students/ | Create a student | 201 |
| GET | /api/students/<id>/ | Student details | 200 |
| PUT | /api/students/<id>/ | Replace a student (all fields) | 200 |
| PATCH | /api/students/<id>/ | Update some fields | 200 |
| DELETE | /api/students/<id>/ | Delete a student | 204 |
| GET, POST | /api/courses/ | List, create a course | 200, 201 |
| GET, PUT, PATCH, DELETE | /api/courses/<id>/ | Course details, update, delete | 200, 200, 200, 204 |

## List options (students)
?page=2  ?page_size=25 (max 50)  ?search=ravi (name or email)
?course=<id>  ?gender=M  ?enrollment_status=enrolled  ?is_active=true  ?ordering=-created_at
Courses: ?status=active  ?search=python  ?ordering=fee
List responses: {"count": 12, "next": "...", "previous": null, "results": [...]}

## Create a student
POST /api/students/
{"full_name": "Ravi Kumar", "email": "ravi@example.com", "mobile_number": "9123456780",
 "gender": "M", "course": 1, "enrollment_status": "enrolled"}
-> 201 with the saved student (including id and course_name)

## Errors (always JSON)
400 {"email": ["student with this email already exists."]}   validation error
401 {"detail": "Authentication credentials were not provided."}
403 {"detail": "You do not have permission to perform this action."}
404 {"detail": "Not found."}
409 {"detail": "This course has enrolled students, so it cannot be deleted."}

## curl example
curl -H "Authorization: Token abc123" http://127.0.0.1:8000/api/students/?search=ravi