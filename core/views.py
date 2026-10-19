
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ContactForm, StudentForm
from .models import Student

from .forms import ContactForm

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


@login_required
def student_list(request):
    students = Student.objects.all()
    return render(request, "students/student_list.html", {"students": students})


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "students/student_detail.html", {"student": student})


@login_required
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"{student.full_name} was registered successfully.")
            return redirect("student_list")
    else:
        form = StudentForm()
    return render(request, "students/student_form.html", {"form": form, "title": "Register Student"})


@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"{student.full_name} was updated successfully.")
            return redirect("student_detail", pk=student.pk)
    else:
        form = StudentForm(instance=student)
    return render(request, "students/student_form.html", {"form": form, "title": "Edit Student"})


@login_required
@require_http_methods(["GET", "POST"])
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        name = student.full_name
        student.delete()
        messages.success(request, f"{name} was deleted.")
        return redirect("student_list")
    return render(request, "students/student_confirm_delete.html", {"student": student})