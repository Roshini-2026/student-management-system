from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.test import Client, TestCase
from django.urls import reverse

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
            "phone": "+919876543210",
            "subject": "Course enquiry",
            "message": "I would like more information.",
        }

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