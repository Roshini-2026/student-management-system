
from django.contrib import messages
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .models import Student,Course, Instructor 
from pathlib import Path
from django.http import FileResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.http import urlencode
from .decorators import permission_needed
from .forms import ContactForm, StudentFilterForm, StudentForm, DashboardFilterForm


COMPANY_NAME = "Student Management Co."


def home(request):
    context = {
        "company_name": COMPANY_NAME,
        "heading": "Welcome to Student Management Co.",
        "intro": "We help institutes manage students, courses and instructors.",
    }
    return render(request, "core/home.html", context)


def about(request):
    context = {
        "company_name": COMPANY_NAME,
        "description": "We build tools that make managing education simple.",
    }
    return render(request, "core/about.html", context)


def services(request):
    service_list = [ {"name": "Student Registration", "description": "Register and manage students.", "featured": True},
            {"name": "Course Management", "description": "Organise courses and instructors.", "featured": False},
            {"name": "Reports", "description": "View statistics and dashboards.", "featured": False},
            ]
    context = {"company_name": COMPANY_NAME, "services": service_list}
    return render(request, "core/services.html", context)


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(
                request,
                "Thank you! Your message has been sent. We will get back to you soon.",
            )
            return redirect("contact")
    else:
        form = ContactForm()

    context = {
        "company_name": COMPANY_NAME,
        "contact_email": "info@example.com",
        "contact_phone": "+91 00000 00000",
        "form": form,
    }
    return render(request, "core/contact.html", context)


def privacy_policy(request):
    return render(request, "core/privacy.html", {"company_name": COMPANY_NAME})


def custom_404(request, exception):
    return render(request, "404.html", {"company_name": COMPANY_NAME}, status=404)


@permission_needed("core.view_student")
def student_list(request):
    filter_form = StudentFilterForm(request.GET)
    filter_form.is_valid()  # runs the checks; invalid values are left out of cleaned_data
    filters = filter_form.cleaned_data

    students = Student.objects.select_related("course")

    search = filters.get("q")
    if search:
        students = students.filter(
            Q(full_name__icontains=search) | Q(email__icontains=search)
        )
    if filters.get("course"):
        students = students.filter(course_id=filters["course"])
    if filters.get("gender"):
        students = students.filter(gender=filters["gender"])

    # "id" is a tie-breaker so the order (and the pages) stay stable
    students = students.order_by(filters.get("sort") or "full_name", "id")

    page_size = int(filters.get("page_size") or 10)
    paginator = Paginator(students, page_size)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Only valid, non-empty values go into the page links
    querystring = urlencode({key: value for key, value in filters.items() if value})

    context = {
        "filter_form": filter_form,
        "page_obj": page_obj,
        "page_range": paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1),
        "ellipsis": paginator.ELLIPSIS,
        "total": paginator.count,
        "querystring": querystring,
        "filters_active": any(filters.get(key) for key in ("q", "course", "gender")),
    }
    return render(request, "students/student_list.html", context)


@permission_needed("core.view_student")
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "students/student_detail.html", {"student": student})


@permission_needed("core.add_student")
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"{student.full_name} was registered successfully.")
            return redirect("student_list")
    else:
        form = StudentForm()
    return render(request, "students/student_form.html", {"form": form, "title": "Register Student"})


@permission_needed("core.change_student")
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"{student.full_name} was updated successfully.")
            return redirect("student_detail", pk=student.pk)
    else:
        form = StudentForm(instance=student)
    return render(request, "students/student_form.html", {"form": form, "title": "Edit Student"})

@permission_needed("core.delete_student")
@require_http_methods(["GET", "POST"])
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        name = student.full_name
        student.delete()
        messages.success(request, f"{name} was deleted.")
        return redirect("student_list")
    return render(request, "students/student_confirm_delete.html", {"student": student})

@permission_needed("core.change_student")
def student_document(request, name):
    """Private documents are only served through this view, after the permission check."""
    student = get_object_or_404(Student, supporting_document=name)
    try:
        file = student.supporting_document.open("rb")
    except FileNotFoundError:
        raise Http404("The file is no longer available.")
    return FileResponse(file, as_attachment=True, filename=f"student-{student.pk}{Path(name).suffix}")

@permission_needed("core.view_reports")
def dashboard(request):
    form = DashboardFilterForm(request.GET or None)
    filters = form.cleaned_data if form.is_valid() else {}  # bad filter values are ignored
    course, date_from, date_to = (filters.get(key) for key in ("course", "date_from", "date_to"))

    students = Student.objects.all()
    date_conditions = Q()  # the same date rules, written for the Course -> students join
    if course:
        students = students.filter(course=course)
    if date_from:
        students = students.filter(created_at__date__gte=date_from)
        date_conditions &= Q(students__created_at__date__gte=date_from)
    if date_to:
        students = students.filter(created_at__date__lte=date_to)
        date_conditions &= Q(students__created_at__date__lte=date_to)

    # order_by() clears the default ordering, which would otherwise break the grouping
    status_totals = dict(students.order_by().values_list("enrollment_status").annotate(Count("id")))
    courses = Course.objects.annotate(student_count=Count("students", filter=date_conditions or None)).order_by("name")
    if course:
        courses = courses.filter(pk=course.pk)
    courses = list(courses)

    context = {
        "form": form,
        "total_students": students.count(),
        "active_courses": Course.objects.filter(status=Course.Status.ACTIVE).count(),
        "total_instructors": Instructor.objects.count(),
        "status_counts": [
            {"label": label, "total": status_totals.get(value, 0)}
            for value, label in Student.EnrollmentStatus.choices
        ],
        "courses": courses,
        "chart_data": {"labels": [c.name for c in courses], "values": [c.student_count for c in courses]},
        "recent_students": students.select_related("course").order_by("-created_at")[:5],
        "recent_activity": students.select_related("course").order_by("-updated_at")[:8],
    }
    return render(request, "dashboard.html", context)