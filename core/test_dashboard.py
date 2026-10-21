from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from .models import Course, Instructor, Student
from .test_utils import make_course, make_student

User = get_user_model()


def aware(year, month, day):
    return timezone.make_aware(datetime(year, month, day, 12))


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", verbosity=0)
        cls.users = {}
        for role in ("Admin", "Staff", "Viewer"):
            user = User.objects.create_user(username=role.lower(), password="pass12345")
            user.groups.add(Group.objects.get(name=role))
            cls.users[role] = user

        cls.python = make_course("PY", "Python")
        cls.java = make_course("JV", "Java")
        make_course("OLD", "Old", status=Course.Status.INACTIVE)
        make_course("EM", "Empty")  # active, but nobody is enrolled
        for n in range(3):
            Instructor.objects.create(full_name=f"Teacher {n}", email=f"t{n}@example.com", specialization="X")

        make_student(cls.python, 1, enrollment_status="enrolled")
        make_student(cls.python, 2, enrollment_status="completed")
        make_student(cls.java, 3, enrollment_status="dropped")
        # Fixed dates, so the order and the date filters are predictable
        dates = {1: (aware(2025, 1, 10), aware(2025, 1, 10)),
                 2: (aware(2025, 3, 1), aware(2025, 7, 1)),
                 3: (aware(2025, 6, 1), aware(2025, 6, 1))}
        for number, (created, updated) in dates.items():
            Student.objects.filter(email=f"student{number}@example.com").update(created_at=created, updated_at=updated)

    def get(self, role="Admin", **params):
        self.client.force_login(self.users[role])
        return self.client.get(reverse("dashboard"), params)

    def test_access_by_role(self):
        for role, status in {"Admin": 200, "Staff": 403, "Viewer": 403}.items():
            with self.subTest(role=role):
                self.assertEqual(self.get(role).status_code, status)

    def test_anonymous_user_is_sent_to_login(self):
        url = reverse("dashboard")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}", fetch_redirect_response=False)

    def test_totals_come_from_the_database(self):
        context = self.get().context
        self.assertEqual(context["total_students"], 3)
        self.assertEqual(context["active_courses"], 3)  # the inactive course is not counted
        self.assertEqual(context["total_instructors"], 3)

    def test_students_per_course_include_empty_courses(self):
        counts = {course.name: course.student_count for course in self.get().context["courses"]}
        self.assertEqual(counts, {"Python": 2, "Java": 1, "Old": 0, "Empty": 0})

    def test_students_grouped_by_status(self):
        totals = {item["label"]: item["total"] for item in self.get().context["status_counts"]}
        self.assertEqual(totals, {"Enrolled": 1, "Completed": 1, "Dropped": 1})

    def test_course_filter(self):
        context = self.get(course=self.java.pk).context
        self.assertEqual(context["total_students"], 1)
        self.assertEqual([course.name for course in context["courses"]], ["Java"])

    def test_date_filter(self):
        context = self.get(date_from="2025-01-01", date_to="2025-03-31").context
        self.assertEqual(context["total_students"], 2)  # students 1 and 2
        counts = {course.name: course.student_count for course in context["courses"]}
        self.assertEqual(counts["Python"], 2)
        self.assertEqual(counts["Java"], 0)

    def test_filters_work_together(self):
        context = self.get(course=self.python.pk, date_from="2025-02-01").context
        self.assertEqual(context["total_students"], 1)  # only student 2

    def test_invalid_date_range_shows_an_error_and_is_ignored(self):
        response = self.get(date_from="2025-02-01", date_to="2025-01-01")
        self.assertContains(response, "start date must be on or before")
        self.assertEqual(response.context["total_students"], 3)

    def test_garbage_filter_values_do_not_crash(self):
        response = self.get(date_from="abc", course="999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_students"], 3)

    def test_recent_lists_are_newest_first(self):
        context = self.get().context
        self.assertEqual([s.full_name for s in context["recent_students"]], ["Student 3", "Student 2", "Student 1"])
        self.assertEqual([s.full_name for s in context["recent_activity"]], ["Student 2", "Student 3", "Student 1"])

    def test_empty_database_is_handled(self):
        Student.objects.all().delete()
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_students"], 0)
        self.assertContains(response, "No student records found")

    def test_dashboard_reflects_new_students(self):
        before = self.get().context["total_students"]
        make_student(self.python, 9)
        self.assertEqual(self.get().context["total_students"], before + 1)

    def test_number_of_queries_does_not_grow_with_data(self):
        self.client.force_login(self.users["Admin"])

        def count_queries():
            with CaptureQueriesContext(connection) as queries:
                self.client.get(reverse("dashboard"))
            return len(queries)

        before = count_queries()
        for n in range(10, 20):
            make_student(make_course(f"C{n}", f"Course {n}"), n)
        self.assertEqual(count_queries(), before)