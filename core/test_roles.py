from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Student

User = get_user_model()


class RolePermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", verbosity=0)
        cls.student = Student.objects.create(
            full_name="Asha Rao", email="asha@example.com", mobile_number="9876543210",
            gender="F", course="Python", address="Hyderabad",
        )
        cls.users = {}
        for role in ("Admin", "Staff", "Viewer"):
            user = User.objects.create_user(username=role.lower(), password="pass12345")
            user.groups.add(Group.objects.get(name=role))
            cls.users[role] = user

    def login_as(self, role):
        self.client.force_login(self.users[role])

    def test_every_role_can_view_students(self):
        for role in self.users:
            with self.subTest(role=role):
                self.login_as(role)
                self.assertEqual(self.client.get(reverse("student_list")).status_code, 200)
                detail = reverse("student_detail", args=[self.student.pk])
                self.assertEqual(self.client.get(detail).status_code, 200)

    def test_page_access_by_role(self):
        pk = self.student.pk
        pages = [("student_create", []), ("student_update", [pk]), ("student_delete", [pk])]
        expected = {"Admin": [200, 200, 200], "Staff": [200, 200, 403], "Viewer": [403, 403, 403]}
        for role, statuses in expected.items():
            self.login_as(role)
            for (name, args), status in zip(pages, statuses):
                with self.subTest(role=role, page=name):
                    self.assertEqual(self.client.get(reverse(name, args=args)).status_code, status)

    def test_viewer_cannot_create_edit_or_delete_by_post(self):
        self.login_as("Viewer")
        pk = self.student.pk
        self.assertEqual(self.client.post(reverse("student_create"), {}).status_code, 403)
        self.assertEqual(self.client.post(reverse("student_update", args=[pk]), {}).status_code, 403)
        self.assertEqual(self.client.post(reverse("student_delete", args=[pk])).status_code, 403)
        self.assertEqual(Student.objects.count(), 1)

    def test_staff_cannot_delete(self):
        self.login_as("Staff")
        response = self.client.post(reverse("student_delete", args=[self.student.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Student.objects.filter(pk=self.student.pk).exists())

    def test_admin_can_delete(self):
        self.login_as("Admin")
        response = self.client.post(reverse("student_delete", args=[self.student.pk]))
        self.assertRedirects(response, reverse("student_list"))
        self.assertFalse(Student.objects.filter(pk=self.student.pk).exists())

    def test_anonymous_user_is_sent_to_login(self):
        url = reverse("student_delete", args=[self.student.pk])
        response = self.client.post(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}", fetch_redirect_response=False)
        self.assertTrue(Student.objects.filter(pk=self.student.pk).exists())

    def test_user_with_no_role_is_denied(self):
        User.objects.create_user(username="norole", password="pass12345")
        self.client.login(username="norole", password="pass12345")
        self.assertEqual(self.client.get(reverse("student_list")).status_code, 403)

    def test_forbidden_page_shows_message(self):
        self.login_as("Viewer")
        response = self.client.get(reverse("student_create"))
        self.assertContains(response, "do not have permission", status_code=403)

    def test_viewer_does_not_see_sensitive_details_or_buttons(self):
        self.login_as("Viewer")
        pk = self.student.pk
        detail = self.client.get(reverse("student_detail", args=[pk]))
        self.assertContains(detail, "asha@example.com")
        self.assertNotContains(detail, "9876543210")
        self.assertNotContains(detail, "Hyderabad")
        listing = self.client.get(reverse("student_list"))
        self.assertNotContains(listing, "9876543210")
        self.assertNotContains(listing, reverse("student_create"))
        self.assertNotContains(listing, reverse("student_update", args=[pk]))
        self.assertNotContains(listing, reverse("student_delete", args=[pk]))

    def test_staff_sees_details_and_edit_but_not_delete(self):
        self.login_as("Staff")
        pk = self.student.pk
        detail = self.client.get(reverse("student_detail", args=[pk]))
        self.assertContains(detail, "9876543210")
        listing = self.client.get(reverse("student_list"))
        self.assertContains(listing, reverse("student_update", args=[pk]))
        self.assertNotContains(listing, reverse("student_delete", args=[pk]))