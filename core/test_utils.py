from .models import Course, Student


def make_course(code="PY", name="Python", **extra):
    return Course.objects.create(name=name, code=code, duration_weeks=8, fee=5000, **extra)


def make_student(course, number=1, **extra):
    return Student.objects.create(
        full_name=f"Student {number}", email=f"student{number}@example.com",
        mobile_number="9876543210", gender="M", course=course, **extra,
    )