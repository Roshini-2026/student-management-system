from smtplib import SMTPException
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Student
from .test_utils import make_course, make_student

User = get_user_model()


class EnrollmentEmailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", verbosity=0)
        cls.course = make_course()
        cls.staff = User.objects.create_user("staff", password="pass12345")
        cls.staff.groups.add(Group.objects.get(name="Staff"))

    def test_email_is_sent_after_the_save_is_committed(self):
        with self.captureOnCommitCallbacks(execute=True):
            make_student(self.course)
        self.assertEqual(len(mail.outbox), 1)

    def test_email_waits_for_the_commit(self):
        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            make_student(self.course)
        self.assertEqual(len(callbacks), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_email_has_the_right_content(self):
        with self.captureOnCommitCallbacks(execute=True):
            student = make_student(self.course)
        message = mail.outbox[0]
        self.assertEqual(message.to, [student.email])
        self.assertIn(self.course.name, message.subject)
        self.assertIn(student.full_name, message.body)
        self.assertIn(settings.SENDER_ADDRESS, message.from_email)
        html = message.alternatives[0].content
        self.assertIn(student.full_name, html)
        self.assertIn(self.course.name, html)

    def test_editing_a_student_does_not_send_another_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            student = make_student(self.course)
        student.full_name = "Changed Name"
        with self.captureOnCommitCallbacks(execute=True):
            student.save()
        self.assertEqual(len(mail.outbox), 1)

    def test_email_failure_keeps_the_student_and_is_logged(self):
        with patch.object(EmailMultiAlternatives, "send", side_effect=SMTPException("server down")):
            with self.assertLogs("core.emails", level="ERROR") as logs:
                with self.captureOnCommitCallbacks(execute=True):
                    student = make_student(self.course)
        self.assertTrue(Student.objects.filter(pk=student.pk).exists())
        self.assertIn(f"student id={student.pk}", logs.output[0])
        self.assertEqual(len(mail.outbox), 0)

    def test_web_registration_sends_one_email_and_a_repeat_sends_none(self):
        self.client.force_login(self.staff)
        data = {
            "full_name": "Asha Rao", "email": "asha@example.com", "mobile_number": "9876543210",
            "gender": "F", "course": self.course.pk, "enrollment_status": "enrolled", "is_active": "on",
        }
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(reverse("student_create"), data)
        self.assertEqual(len(mail.outbox), 1)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse("student_create"), data)  # repeated request
        self.assertEqual(response.status_code, 200)  # rejected: the email already exists
        self.assertEqual(len(mail.outbox), 1)

    def test_invalid_registration_sends_no_email(self):
        self.client.force_login(self.staff)
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(reverse("student_create"), {})
        self.assertEqual(len(mail.outbox), 0)