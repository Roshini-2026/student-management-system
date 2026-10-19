from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.test import Client, TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Student

class PageTests(TestCase):
    def test_pages_load(self):
        for name in ["home", "about", "services", "contact", "privacy"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)

    def test_pages_use_base_layout(self):
        response = self.client.get(reverse("about"))
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Services")  

    def test_static_files_are_linked(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "css/style.css")
        self.assertContains(response, "js/main.js")

    def test_invalid_url_returns_404(self):
        response = self.client.get("/does-not-exist/")
        self.assertEqual(response.status_code, 404)

class ContactFormTests(TestCase):
    def setUp(self):
        self.url = reverse("contact")
        self.valid_data = {
            "full_name": "Asha Rao",
            "email": "asha@example.com",
            "phone": "1234567890",
            "subject": "Course enquiry",
            "message": "I would like more information.",
        }
    def test_phone_must_be_exactly_10_digits(self):
        for bad in ["12345", "12345678901", "+911234567890", "12345 67890"]:
            response = self.client.post(self.url, {**self.valid_data, "phone": bad})
            self.assertIn("phone", response.context["form"].errors, bad)

    def test_phone_error_message(self):
        response = self.client.post(self.url, {**self.valid_data, "phone": "123"})
        self.assertContains(response, "The number should contain 10 digits.")

    def test_get_shows_form_with_csrf_token(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_valid_submission_redirects_with_success_message(self):
        response = self.client.post(self.url, self.valid_data, follow=True)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Your message has been sent")

    def test_phone_is_optional(self):
        data = {**self.valid_data, "phone": ""}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

    def test_empty_submission_is_rejected(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        errors = response.context["form"].errors
        for field in ["full_name", "email", "subject", "message"]:
            self.assertIn(field, errors)
        self.assertNotIn("phone", errors)

    def test_invalid_email_is_rejected(self):
        data = {**self.valid_data, "email": "not-an-email"}
        response = self.client.post(self.url, data)
        self.assertIn("email", response.context["form"].errors)

    def test_invalid_phone_is_rejected(self):
        data = {**self.valid_data, "phone": "abc123"}
        response = self.client.post(self.url, data)
        self.assertIn("phone", response.context["form"].errors)

    def test_entered_values_are_preserved_on_error(self):
        data = {**self.valid_data, "email": "bad"}
        response = self.client.post(self.url, data)
        self.assertContains(response, 'value="Asha Rao"')

    def test_csrf_protection_is_enforced(self):
        strict_client = Client(enforce_csrf_checks=True)
        response = strict_client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 403)
class StudentModelTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            full_name="Asha Rao", email="asha@example.com",
            mobile_number="9876543210", gender="F", course="Python",
        )

    def test_string_representation(self):
        self.assertEqual(str(self.student), "Asha Rao (asha@example.com)")

    def test_duplicate_email_is_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Student.objects.create(
                full_name="Other", email="asha@example.com",
                mobile_number="1234567890", gender="M", course="Django",
            )

    def test_required_field_is_enforced(self):
        student = Student(email="x@example.com", mobile_number="1", gender="M", course="C")
        with self.assertRaises(ValidationError):
            student.full_clean()

    def test_optional_fields_can_be_empty(self):
        self.assertIsNone(self.student.date_of_birth)
        self.assertEqual(self.student.address, "")

    def test_timestamps_are_set(self):
        self.assertIsNotNone(self.student.created_at)
        self.assertIsNotNone(self.student.updated_at)

    def test_default_ordering_is_by_name(self):
        Student.objects.create(
            full_name="Anil Das", email="anil@example.com",
            mobile_number="1234567890", gender="M", course="Java",
        )
        names = list(Student.objects.values_list("full_name", flat=True))
        self.assertEqual(names, ["Anil Das", "Asha Rao"])

class StudentCrudTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester", password="pass12345")
        self.client.force_login(self.user)
        self.student = Student.objects.create(
            full_name="Asha Rao", email="asha@example.com",
            mobile_number="9876543210", gender="F", course="Python",
        )
        self.valid_data = {
            "full_name": "Ravi Kumar", "email": "ravi@example.com",
            "mobile_number": "9123456780", "gender": "M",
            "course": "Django", "is_active": "on",
        }

    def test_student_mobile_must_be_10_digits(self):
        data = {**self.valid_data, "mobile_number": "12345"}
        response = self.client.post(reverse("student_create"), data)
        self.assertIn("mobile_number", response.context["form"].errors)

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()
        url = reverse("student_list")
        response = self.client.get(url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={url}", fetch_redirect_response=False)

    def test_list_shows_students(self):
        response = self.client.get(reverse("student_list"))
        self.assertContains(response, "Asha Rao")

    def test_list_empty_state(self):
        Student.objects.all().delete()
        response = self.client.get(reverse("student_list"))
        self.assertContains(response, "No students have been registered yet")

    def test_create_valid_student(self):
        response = self.client.post(reverse("student_create"), self.valid_data, follow=True)
        self.assertRedirects(response, reverse("student_list"))
        self.assertTrue(Student.objects.filter(email="ravi@example.com").exists())
        self.assertContains(response, "registered successfully")

    def test_create_duplicate_email_is_rejected(self):
        data = {**self.valid_data, "email": "asha@example.com"}
        response = self.client.post(reverse("student_create"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)
        self.assertEqual(Student.objects.count(), 1)

    def test_create_missing_fields_is_rejected(self):
        response = self.client.post(reverse("student_create"), {})
        self.assertIn("full_name", response.context["form"].errors)
        self.assertEqual(Student.objects.count(), 1)

    def test_detail_page(self):
        response = self.client.get(reverse("student_detail", args=[self.student.pk]))
        self.assertContains(response, "asha@example.com")

    def test_detail_of_missing_student_returns_404(self):
        response = self.client.get(reverse("student_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_update_student(self):
        data = {**self.valid_data, "email": "asha@example.com", "full_name": "Asha Updated"}
        response = self.client.post(reverse("student_update", args=[self.student.pk]), data)
        self.assertRedirects(response, reverse("student_detail", args=[self.student.pk]))
        self.student.refresh_from_db()
        self.assertEqual(self.student.full_name, "Asha Updated")

    def test_delete_get_only_shows_confirmation(self):
        response = self.client.get(reverse("student_delete", args=[self.student.pk]))
        self.assertContains(response, "Are you sure")
        self.assertTrue(Student.objects.filter(pk=self.student.pk).exists())

    def test_delete_post_removes_student(self):
        response = self.client.post(reverse("student_delete", args=[self.student.pk]))
        self.assertRedirects(response, reverse("student_list"))
        self.assertFalse(Student.objects.filter(pk=self.student.pk).exists())

    def test_delete_missing_student_returns_404(self):
        response = self.client.post(reverse("student_delete", args=[9999]))
        self.assertEqual(response.status_code, 404)