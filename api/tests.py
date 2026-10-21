from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase

from core.models import Course, Student
from core.test_utils import make_course, make_student

User = get_user_model()
PASSWORD = "pass12345"


class ApiTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", verbosity=0)
        for role in ("Admin", "Staff", "Viewer"):
            user = User.objects.create_user(username=role.lower(), password=PASSWORD)
            user.groups.add(Group.objects.get(name=role))
        cls.course = make_course()
        cls.student = make_student(cls.course, 1)

    def as_role(self, role):
        self.client.force_authenticate(User.objects.get(username=role.lower()))

    def student_payload(self, **extra):
        return {
            "full_name": "Ravi Kumar", "email": "ravi@example.com", "mobile_number": "9123456780",
            "gender": "M", "course": self.course.pk, "enrollment_status": "enrolled", **extra,
        }

    def course_payload(self, **extra):
        return {"name": "Django", "code": "DJ", "description": "", "duration_weeks": 6,
                "fee": "4000.00", "status": "active", **extra}


class AuthenticationTests(ApiTestCase):
    def test_token_login_and_use(self):
        response = self.client.post("/api/token/", {"username": "viewer", "password": PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        self.assertEqual(self.client.get("/api/students/").status_code, 200)

    def test_wrong_credentials_get_no_token(self):
        response = self.client.post("/api/token/", {"username": "viewer", "password": "wrong"})
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("token", response.data)

    def test_unauthenticated_requests_are_rejected(self):
        for url in ("/api/students/", "/api/courses/", f"/api/students/{self.student.pk}/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 401)


class StudentApiTests(ApiTestCase):
    def test_list_is_paginated(self):
        for n in range(2, 13):
            make_student(self.course, n)
        self.as_role("Viewer")
        response = self.client.get("/api/students/", {"page_size": 5})
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])

    def test_invalid_page_returns_404(self):
        self.as_role("Viewer")
        self.assertEqual(self.client.get("/api/students/", {"page": 999}).status_code, 404)

    def test_viewer_does_not_see_private_fields_but_staff_does(self):
        self.as_role("Viewer")
        viewer_item = self.client.get("/api/students/").data["results"][0]
        self.assertNotIn("mobile_number", viewer_item)
        self.assertNotIn("address", viewer_item)
        self.as_role("Staff")
        self.assertIn("mobile_number", self.client.get("/api/students/").data["results"][0])

    def test_search_filter_and_ordering(self):
        make_student(self.course, 2, gender="F")
        make_student(make_course("JV", "Java"), 3)
        self.as_role("Admin")
        self.assertEqual(self.client.get("/api/students/", {"search": "student2@"}).data["count"], 1)
        self.assertEqual(self.client.get("/api/students/", {"gender": "F"}).data["count"], 1)
        self.assertEqual(self.client.get("/api/students/", {"course": self.course.pk}).data["count"], 2)
        first = self.client.get("/api/students/", {"ordering": "-full_name"}).data["results"][0]
        self.assertEqual(first["full_name"], "Student 3")
        self.assertEqual(self.client.get("/api/students/", {"course": "abc"}).status_code, 400)

    def test_retrieve_one_and_missing_and_invalid_ids(self):
        self.as_role("Viewer")
        self.assertEqual(self.client.get(f"/api/students/{self.student.pk}/").data["email"], self.student.email)
        self.assertEqual(self.client.get("/api/students/9999/").status_code, 404)
        self.assertEqual(self.client.get("/api/students/abc/").status_code, 404)

    def test_staff_can_create(self):
        self.as_role("Staff")
        response = self.client.post("/api/students/", self.student_payload())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["course_name"], "Python")
        self.assertTrue(Student.objects.filter(email="ravi@example.com").exists())

    def test_viewer_cannot_create(self):
        self.as_role("Viewer")
        self.assertEqual(self.client.post("/api/students/", self.student_payload()).status_code, 403)
        self.assertEqual(Student.objects.count(), 1)

    def test_missing_fields_return_validation_errors(self):
        self.as_role("Staff")
        response = self.client.post("/api/students/", {})
        self.assertEqual(response.status_code, 400)
        for field in ("full_name", "email", "mobile_number", "gender", "course"):
            self.assertIn(field, response.data)

    def test_invalid_values_are_rejected(self):
        inactive = make_course("OLD", "Old", status=Course.Status.INACTIVE)
        bad_payloads = {
            "email": self.student_payload(email=self.student.email),  # duplicate
            "mobile_number": self.student_payload(mobile_number="12345"),
            "course": self.student_payload(course=inactive.pk),
        }
        self.as_role("Staff")
        for field, payload in bad_payloads.items():
            with self.subTest(field=field):
                response = self.client.post("/api/students/", payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.assertEqual(Student.objects.count(), 1)

    def test_malformed_json_returns_400(self):
        self.as_role("Staff")
        response = self.client.post("/api/students/", "{bad json", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_put_and_patch(self):
        url = f"/api/students/{self.student.pk}/"
        self.as_role("Staff")
        put = self.client.put(url, self.student_payload(email=self.student.email))
        self.assertEqual(put.status_code, 200)
        patch = self.client.patch(url, {"full_name": "Patched Name"})
        self.assertEqual(patch.data["full_name"], "Patched Name")
        self.as_role("Viewer")
        self.assertEqual(self.client.patch(url, {"full_name": "Hacked"}).status_code, 403)
        self.student.refresh_from_db()
        self.assertEqual(self.student.full_name, "Patched Name")

    def test_only_admin_can_delete(self):
        url = f"/api/students/{self.student.pk}/"
        self.as_role("Staff")
        self.assertEqual(self.client.delete(url).status_code, 403)
        self.assertTrue(Student.objects.filter(pk=self.student.pk).exists())
        self.as_role("Admin")
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertFalse(Student.objects.filter(pk=self.student.pk).exists())

    def test_list_does_not_run_a_query_per_row(self):
        def count_queries():
            self.as_role("Admin")  # a fresh user each time, so permission lookups are counted equally
            with CaptureQueriesContext(connection) as queries:
                self.client.get("/api/students/")
            return len(queries)

        before = count_queries()
        for n in range(2, 8):
            make_student(make_course(f"C{n}", f"Course {n}"), n)
        self.assertEqual(count_queries(), before)


class CourseApiTests(ApiTestCase):
    def test_access_by_role(self):
        expected = {"Admin": 200, "Staff": 200, "Viewer": 403}
        for role, status in expected.items():
            with self.subTest(role=role):
                self.as_role(role)
                self.assertEqual(self.client.get("/api/courses/").status_code, status)

    def test_list_and_detail_show_student_counts(self):
        self.as_role("Staff")
        self.assertEqual(self.client.get("/api/courses/").data["results"][0]["student_count"], 1)
        self.assertEqual(self.client.get(f"/api/courses/{self.course.pk}/").data["student_count"], 1)

    def test_only_admin_can_create_update_and_delete(self):
        self.as_role("Staff")
        self.assertEqual(self.client.post("/api/courses/", self.course_payload()).status_code, 403)
        self.assertEqual(self.client.patch(f"/api/courses/{self.course.pk}/", {"fee": "1.00"}).status_code, 403)
        self.as_role("Admin")
        created = self.client.post("/api/courses/", self.course_payload())
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["student_count"], 0)
        patched = self.client.patch(f"/api/courses/{created.data['id']}/", {"fee": "4500.00"})
        self.assertEqual(patched.data["fee"], "4500.00")
        self.assertEqual(self.client.delete(f"/api/courses/{created.data['id']}/").status_code, 204)

    def test_invalid_course_is_rejected(self):
        self.as_role("Admin")
        response = self.client.post("/api/courses/", self.course_payload(fee="-5", duration_weeks=0))
        self.assertEqual(response.status_code, 400)
        self.assertIn("fee", response.data)
        self.assertIn("duration_weeks", response.data)

    def test_course_with_students_cannot_be_deleted(self):
        self.as_role("Admin")
        response = self.client.delete(f"/api/courses/{self.course.pk}/")
        self.assertEqual(response.status_code, 409)
        self.assertTrue(Course.objects.filter(pk=self.course.pk).exists())

    def test_missing_course_returns_404(self):
        self.as_role("Admin")
        self.assertEqual(self.client.get("/api/courses/9999/").status_code, 404)

    def test_search_and_status_filter(self):
        make_course("OLD", "Old", status=Course.Status.INACTIVE)
        self.as_role("Admin")
        self.assertEqual(self.client.get("/api/courses/", {"search": "Old"}).data["count"], 1)
        self.assertEqual(self.client.get("/api/courses/", {"status": "active"}).data["count"], 1)