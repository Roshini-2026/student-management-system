
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import Group

from core.forms import BootstrapFormMixin

User = get_user_model()


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["first_name", "last_name", "username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["email"].required = True

    def clean_email(self):
        """Email policy: one account per email address, ignoring upper/lower case."""
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            viewer_group, _ = Group.objects.get_or_create(name="Viewer")
            user.groups.add(viewer_group)  # new users start with the least access
        return user


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass


class ChangePasswordForm(BootstrapFormMixin, PasswordChangeForm):
    pass


class ResetRequestForm(BootstrapFormMixin, PasswordResetForm):
    pass


class SetNewPasswordForm(BootstrapFormMixin, SetPasswordForm):
    pass