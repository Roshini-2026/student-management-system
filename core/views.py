
from django.contrib import messages
from django.shortcuts import redirect, render

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