from django.test import TestCase

# Create your tests here.
from django.test import TestCase
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