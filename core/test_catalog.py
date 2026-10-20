from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from .forms import StudentForm
from .models import Course, Instructor, Student
from .test_utils import make_course, make_student

User = get_user_model()


class RelationshipTests(TestCase):
    def test_course_code_must_be_unique(self):
        make_course()
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_course(name="Other")  # same code "PY"

    def test_invalid_fee_and_duration_are_rejected(self):
        course = Course(name="X", code="X1", duration_weeks=0, fee=-1)
        with self.assertRaises(ValidationError) as caught:
            course.full_clean()
        self.assertIn("fee", caught.exception.message_dict)
        self.assertIn("duration_weeks", caught.exception.message_dict)

    def test_course_with_students_cannot_be_deleted(self):
        course = make_course()
        make_student(course)
        with self.assertRaises(ProtectedError):
            course.delete()

    def test_course_without_students_can_be_deleted(self):
        make_course().delete()
        self.assertEqual(Course.objects.count(), 0)

    def test_instructors_and_courses_are_many_to_many(self):
        python, django = make_course("PY", "Python"), make_course("DJ", "Django")
        ravi = Instructor.objects.create(full_name="Ravi", email="r@example.com", specialization="Python")
        python.instructors.add(ravi)
        django.instructors.add(ravi)
        self.assertEqual(ravi.courses.count(), 2)

    def test_deleting_instructor_keeps_the_course(self):
        course = make_course()
        ravi = Instructor.objects.create(full_name="Ravi", email="r@example.com", specialization="Python")
        course.instructors.add(ravi)
        ravi.delete()
        self.assertTrue(Course.objects.filter(pk=course.pk).exists())
        self.assertEqual(course.instructors.count(), 0)

    def test_instructor_email_must_be_unique(self):
        Instructor.objects.create(full_name="A", email="a@example.com", specialization="X")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Instructor.objects.create(full_name="B", email="a@example.com", specialization="Y")

    def test_inactive_course_cannot_be_chosen_for_a_student(self):
        inactive = make_course("OLD", "Old", status=Course.Status.INACTIVE)
        form = StudentForm(data={"course": inactive.pk})
        self.assertFalse(form.is_valid())
        self.assertIn("course", form.errors)


class CatalogViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", verbosity=0)
        cls.users = {}
        for role in ("Admin", "Staff", "Viewer"):
            user = User.objects.create_user(username=role.lower(), password="pass12345")
            user.groups.add(Group.objects.get(name=role))
            cls.users[role] = user
        cls.course = make_course()
        make_student(cls.course, 1)
        make_student(cls.course, 2)

    def login_as(self, role):
        self.client.force_login(self.users[role])

    def count_queries(self, url):
        with CaptureQueriesContext(connection) as queries:
            self.client.get(url)
        return len(queries)

    def test_course_list_shows_student_count(self):
        self.login_as("Staff")
        response = self.client.get(reverse("course_list"))
        self.assertEqual(response.context["courses"][0].student_count, 2)

    def test_course_detail_lists_enrolled_students(self):
        self.login_as("Staff")
        response = self.client.get(reverse("course_detail", args=[self.course.pk]))
        self.assertContains(response, "Student 1")
        self.assertContains(response, "Student 2")

    def test_student_detail_shows_course(self):
        self.login_as("Staff")
        student = Student.objects.first()
        response = self.client.get(reverse("student_detail", args=[student.pk]))
        self.assertContains(response, "PY - Python")

    def test_access_by_role(self):
        pages = ["course_list", "course_create", "instructor_list"]
        expected = {"Admin": [200, 200, 200], "Staff": [200, 403, 403], "Viewer": [403, 403, 403]}
        for role, statuses in expected.items():
            self.login_as(role)
            for page, status in zip(pages, statuses):
                with self.subTest(role=role, page=page):
                    self.assertEqual(self.client.get(reverse(page)).status_code, status)

    def test_anonymous_user_is_sent_to_login(self):
        url = reverse("course_list")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}", fetch_redirect_response=False)

    def test_admin_can_create_course(self):
        self.login_as("Admin")
        data = {"name": "Django", "code": "DJ", "description": "", "duration_weeks": 6,
                "fee": "4000.00", "status": "active"}
        response = self.client.post(reverse("course_create"), data)
        self.assertRedirects(response, reverse("course_list"))
        self.assertTrue(Course.objects.filter(code="DJ").exists())

    def test_staff_cannot_create_course(self):
        self.login_as("Staff")
        self.assertEqual(self.client.post(reverse("course_create"), {}).status_code, 403)

    def test_invalid_course_is_rejected(self):
        self.login_as("Admin")
        data = {"name": "Bad", "code": "BD", "duration_weeks": 6, "fee": "-5", "status": "active"}
        response = self.client.post(reverse("course_create"), data)
        self.assertIn("fee", response.context["form"].errors)
        self.assertFalse(Course.objects.filter(code="BD").exists())

    def test_course_with_students_cannot_be_deleted_from_the_page(self):
        self.login_as("Admin")
        response = self.client.post(reverse("course_delete", args=[self.course.pk]), follow=True)
        self.assertContains(response, "cannot be deleted")
        self.assertTrue(Course.objects.filter(pk=self.course.pk).exists())

    def test_empty_course_can_be_deleted_from_the_page(self):
        empty = make_course("EM", "Empty")
        self.login_as("Admin")
        self.client.post(reverse("course_delete", args=[empty.pk]))
        self.assertFalse(Course.objects.filter(pk=empty.pk).exists())

    def test_missing_course_returns_404(self):
        self.login_as("Admin")
        self.assertEqual(self.client.get(reverse("course_detail", args=[9999])).status_code, 404)

    def test_list_pages_do_not_run_a_query_per_row(self):
        self.login_as("Admin")
        urls = [reverse("course_list"), reverse("student_list")]
        before = [self.count_queries(url) for url in urls]
        for n in range(3, 8):
            make_student(make_course(f"C{n}", f"Course {n}"), n)
        after = [self.count_queries(url) for url in urls]
        self.assertEqual(before, after)


class AdminSiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course = make_course()
        cls.student = make_student(cls.course)
        cls.superuser = User.objects.create_superuser("root", "root@example.com", "pass12345")

    def test_non_staff_users_cannot_open_admin(self):
        self.client.force_login(User.objects.create_user("viewer", password="pass12345"))
        response = self.client.get("/admin/core/student/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_student_admin_search(self):
        self.client.force_login(self.superuser)
        response = self.client.get("/admin/core/student/", {"q": "Student 1"})
        self.assertContains(response, "Student 1")

    def test_student_admin_groups_fields_into_sections(self):
        self.client.force_login(self.superuser)
        response = self.client.get(f"/admin/core/student/{self.student.pk}/change/")
        self.assertContains(response, "System information")

    def test_course_admin_shows_student_counts(self):
        self.client.force_login(self.superuser)
        response = self.client.get("/admin/core/course/")
        self.assertEqual(response.context["cl"].result_list[0]._student_count, 1)

    def test_bulk_action_marks_students_completed(self):
        self.client.force_login(self.superuser)
        data = {"action": "mark_completed", "_selected_action": [self.student.pk]}
        self.client.post("/admin/core/student/", data, follow=True)
        self.student.refresh_from_db()
        self.assertEqual(self.student.enrollment_status, "completed")