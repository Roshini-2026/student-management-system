from django.urls import path
from django.views.generic import TemplateView

from . import views

MESSAGE_TEMPLATE = "accounts/message.html"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.LoginPage.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("password-change/", views.PasswordChangePage.as_view(), name="password_change"),
    path("password-reset/", views.PasswordResetPage.as_view(), name="password_reset"),
    path(
        "password-reset/sent/",
        TemplateView.as_view(
            template_name=MESSAGE_TEMPLATE,
            extra_context={
                "title": "Check your email",
                "text": "If an account exists for that email address, we have sent instructions to reset the password.",
            },
        ),
        name="password_reset_done",
    ),
    path("reset/<uidb64>/<token>/", views.PasswordResetConfirmPage.as_view(), name="password_reset_confirm"),
    path(
        "reset/done/",
        TemplateView.as_view(
            template_name=MESSAGE_TEMPLATE,
            extra_context={"title": "Password changed", "text": "Your password was changed. You can log in now."},
        ),
        name="password_reset_complete",
    ),
]