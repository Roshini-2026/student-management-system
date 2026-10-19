from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()
PASSWORD = "Str0ng-Pass-99"
NEW_PASSWORD = "Another-Pass-77"


class RegistrationTests(TestCase):
    def setUp(self):
        self.url = reverse("register")
        self.valid_data = {
            "first_name": "Asha", "last_name": "Rao", "username": "asha",
            "email": "asha@example.com", "password1": PASSWORD, "password2": PASSWORD,
        }

    def test_valid_registration(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, reverse("login"))
        user = User.objects.get(username="asha")
        self.assertNotEqual(user.password, PASSWORD)  # never stored as plain text
        self.assertTrue(user.check_password(PASSWORD))
        self.assertTrue(user.groups.filter(name="Viewer").exists())

    def test_missing_fields_are_rejected(self):
        response = self.client.post(self.url, {})
        errors = response.context["form"].errors
        for field in ["first_name", "username", "email", "password1", "password2"]:
            self.assertIn(field, errors)
        self.assertEqual(User.objects.count(), 0)

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user("asha", "other@example.com", PASSWORD)
        response = self.client.post(self.url, self.valid_data)
        self.assertIn("username", response.context["form"].errors)

    def test_duplicate_email_is_rejected_ignoring_case(self):
        User.objects.create_user("someone", "ASHA@Example.com", PASSWORD)
        response = self.client.post(self.url, self.valid_data)
        self.assertIn("email", response.context["form"].errors)

    def test_password_mismatch_is_rejected(self):
        data = {**self.valid_data, "password2": "Different-Pass-1"}
        response = self.client.post(self.url, data)
        self.assertIn("password2", response.context["form"].errors)

    def test_weak_password_is_rejected(self):
        data = {**self.valid_data, "password1": "12345678", "password2": "12345678"}
        response = self.client.post(self.url, data)
        self.assertIn("password2", response.context["form"].errors)


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("asha", "asha@example.com", PASSWORD, first_name="Asha")
        self.login_url = reverse("login")

    def test_valid_login(self):
        response = self.client.post(self.login_url, {"username": "asha", "password": PASSWORD}, follow=True)
        self.assertRedirects(response, reverse("home"))
        self.assertContains(response, "Welcome back")
        self.assertIn("_auth_user_id", self.client.session)

    def test_invalid_login_is_rejected(self):
        response = self.client.post(self.login_url, {"username": "asha", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_error_does_not_reveal_which_part_was_wrong(self):
        wrong_password = self.client.post(self.login_url, {"username": "asha", "password": "wrong"})
        unknown_user = self.client.post(self.login_url, {"username": "nobody", "password": "wrong"})
        self.assertEqual(
            list(wrong_password.context["form"].non_field_errors()),
            list(unknown_user.context["form"].non_field_errors()),
        )

    def test_logout_ends_the_session(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_by_link_is_not_allowed(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)

    def test_profile_requires_login(self):
        url = reverse("profile")
        response = self.client.get(url)
        self.assertRedirects(response, f"{self.login_url}?next={url}", fetch_redirect_response=False)

    def test_profile_shows_user_details(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("profile"))
        self.assertContains(response, "asha@example.com")


class PasswordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("asha", "asha@example.com", PASSWORD)

    def test_change_password(self):
        self.client.force_login(self.user)
        data = {"old_password": PASSWORD, "new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD}
        response = self.client.post(reverse("password_change"), data)
        self.assertRedirects(response, reverse("profile"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))

    def test_change_password_with_wrong_old_password(self):
        self.client.force_login(self.user)
        data = {"old_password": "wrong", "new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD}
        response = self.client.post(reverse("password_change"), data)
        self.assertIn("old_password", response.context["form"].errors)

    def test_change_password_requires_login(self):
        response = self.client.get(reverse("password_change"))
        self.assertEqual(response.status_code, 302)

    def test_reset_sends_email_for_known_address(self):
        response = self.client.post(reverse("password_reset"), {"email": "asha@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/reset/", mail.outbox[0].body)

    def test_reset_for_unknown_address_looks_the_same_but_sends_nothing(self):
        response = self.client.post(reverse("password_reset"), {"email": "nobody@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)