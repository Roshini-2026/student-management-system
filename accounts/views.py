from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .forms import (
    ChangePasswordForm, LoginForm, RegisterForm, ResetRequestForm, SetNewPasswordForm,
)

FORM_TEMPLATE = "accounts/form.html"


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account was created. You can log in now.")
            return redirect("login")
    else:
        form = RegisterForm()
    context = {"form": form, "title": "Create an account", "button": "Register"}
    return render(request, FORM_TEMPLATE, context)


class LoginPage(SuccessMessageMixin, LoginView):
    template_name = FORM_TEMPLATE
    authentication_form = LoginForm
    redirect_authenticated_user = True
    success_message = "Welcome back!"
    extra_context = {"title": "Log in", "button": "Log in"}


@require_POST
def logout_view(request):
    logout(request)  # ends the session
    messages.success(request, "You have been logged out.")
    return redirect("login")


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


class PasswordChangePage(SuccessMessageMixin, PasswordChangeView):
    template_name = FORM_TEMPLATE
    form_class = ChangePasswordForm
    success_url = reverse_lazy("profile")
    success_message = "Your password was changed."
    extra_context = {"title": "Change password", "button": "Change password"}


class PasswordResetPage(PasswordResetView):
    template_name = FORM_TEMPLATE
    form_class = ResetRequestForm
    email_template_name = "accounts/password_reset_email.txt"
    success_url = reverse_lazy("password_reset_done")
    extra_context = {"title": "Reset your password", "button": "Send reset link"}


class PasswordResetConfirmPage(PasswordResetConfirmView):
    template_name = FORM_TEMPLATE
    form_class = SetNewPasswordForm
    success_url = reverse_lazy("password_reset_complete")
    extra_context = {"title": "Choose a new password", "button": "Change password"}