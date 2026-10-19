from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

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
    context = {
        "company_name": COMPANY_NAME,
        "contact_email": "info@example.com",
        "contact_phone": "+91 00000 00000",
    }
    return render(request, "core/contact.html", context)


def privacy_policy(request):
    return render(request, "core/privacy.html", {"company_name": COMPANY_NAME})


def custom_404(request, exception):
    return render(request, "404.html", {"company_name": COMPANY_NAME}, status=404)