from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Student
from .test_utils import make_course, make_student

User = get_user_model()
PASSWORD = "pass12345"


class SecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", verbosity=0)
        cls.student = make_student(make_course())
        cls.admin = User.objects.create_superuser("root", "root@example.com", PASSWORD)
        cls.viewer = User.objects.create_user("viewer", password=PASSWORD)
        cls.viewer.groups.add(Group.objects.get(name="Viewer"))

    def test_forms_include_csrf_tokens(self):
        pk = self.student.pk
        self.client.force_login(self.admin)
        for url in (reverse("student_create"), reverse("student_update", args=[pk]),
                    reverse("student_delete", args=[pk]), reverse("course_create"),
                    reverse("password_change")):
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), "csrfmiddlewaretoken")
        self.client.logout()
        for name in ("login", "register", "password_reset", "contact"):
            with self.subTest(page=name):
                self.assertContains(self.client.get(reverse(name)), "csrfmiddlewaretoken")

    def test_post_without_csrf_token_is_rejected(self):
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.admin)
        response = strict.post(reverse("student_delete", args=[self.student.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Student.objects.filter(pk=self.student.pk).exists())

    def test_session_cookie_is_http_only(self):
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.client.post(reverse("login"), {"username": "viewer", "password": PASSWORD})
        self.assertTrue(self.client.cookies[settings.SESSION_COOKIE_NAME]["httponly"])

    def test_viewer_cannot_read_private_fields_through_the_api(self):
        api = APIClient()
        api.force_authenticate(self.viewer)
        for url in ("/api/students/", f"/api/students/{self.student.pk}/"):
            with self.subTest(url=url):
                data = api.get(url).data
                item = data["results"][0] if "results" in data else data
                for field in ("mobile_number", "date_of_birth", "address"):
                    self.assertNotIn(field, item)

    def test_server_errors_do_not_show_internal_details(self):
        client = Client(raise_request_exception=False)
        client.force_login(self.admin)
        with patch("core.views.StudentFilterForm", side_effect=RuntimeError("secret internal detail")):
            with self.assertLogs("django.request", level="ERROR"):
                response = client.get(reverse("student_list"))
        self.assertEqual(response.status_code, 500)
        self.assertNotContains(response, "secret internal detail", status_code=500)
        self.assertNotContains(response, "Traceback", status_code=500)