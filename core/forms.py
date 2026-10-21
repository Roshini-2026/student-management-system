import re

from django import forms
from django.db.models import Q

from .models import Course, Instructor, Student
PHONE_ERROR = "Enter a valid phone number. The number should contain 10 digits."

# Extra HTML attributes for phone inputs: numeric keypad on mobile, max 10 characters
PHONE_ATTRS = {
    "maxlength": "10",
    "inputmode": "numeric",
    "pattern": "[0-9]{10}",
    "placeholder": "10-digit number",
    "title": "Enter a 10-digit phone number",
}


def clean_phone_number(value):
    """Accept only exactly 10 digits (an empty value is allowed here; the field decides if it's required)."""
    value = value.strip()
    if value and not re.fullmatch(r"[0-9]{10}", value):
        raise forms.ValidationError(PHONE_ERROR)
    return value


class BootstrapFormMixin:
    """Adds Bootstrap classes to every field, and a red border to fields with errors."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = "form-select"
            else:
                widget.attrs["class"] = "form-control"
            if name in ("phone", "mobile_number"):
                widget.attrs.update(PHONE_ATTRS)

    def full_clean(self):
        super().full_clean()  # run Django's normal validation first
        for name in self.errors:
            if name in self.fields:  # "__all__" (form-level errors) is not a field
                self.fields[name].widget.attrs["class"] += " is-invalid"


class ContactForm(BootstrapFormMixin, forms.Form):
    full_name = forms.CharField(max_length=100, label="Full name")
    email = forms.EmailField(label="Email address")
    phone = forms.CharField(max_length=10, required=False, label="Phone number")
    subject = forms.CharField(max_length=150, label="Subject")
    message = forms.CharField(
        max_length=2000,
        label="Message",
        widget=forms.Textarea(attrs={"rows": 5}),
    )

    def clean_phone(self):
        return clean_phone_number(self.cleaned_data["phone"])


class StudentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "full_name", "email", "mobile_number", "gender", "date_of_birth",
            "course", "enrollment_status", "address", "is_active",
            "profile_photo", "supporting_document"
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "profile_photo": forms.ClearableFileInput(attrs={"accept": "image/png,image/jpeg"}),
            "supporting_document": forms.ClearableFileInput(attrs={"accept": "application/pdf"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only active courses can be chosen. When editing, the student's current course stays.
        allowed = Q(status=Course.Status.ACTIVE)
        if self.instance.course_id:
            allowed |= Q(pk=self.instance.course_id)
        self.fields["course"].queryset = Course.objects.filter(allowed)

    def clean_mobile_number(self):
        return clean_phone_number(self.cleaned_data["mobile_number"])


class CourseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "code", "description", "duration_weeks", "fee", "status", "instructors"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class InstructorForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ["full_name", "email", "specialization"]

def get_course_choices():
    """Course dropdown options, read from the database when the form is validated or shown."""
    return [("", "All courses"), *Course.objects.values_list("pk", "name")]

class StudentFilterForm(BootstrapFormMixin, forms.Form):
    SORT_CHOICES = [
        ("full_name", "Name (A-Z)"),
        ("-full_name", "Name (Z-A)"),
        ("-created_at", "Newest registered"),
        ("created_at", "Oldest registered"),
    ]
    PAGE_SIZE_CHOICES = [("10", "10"), ("25", "25"), ("50", "50")]

    q = forms.CharField(max_length=100, required=False, label="Search")
    course = forms.ChoiceField(choices=get_course_choices, required=False, label="Course")
    gender = forms.ChoiceField(
        required=False, label="Gender",
        choices=[("", "All genders")] + Student.Gender.choices,
    )
    sort = forms.ChoiceField(required=False, label="Sort by", choices=SORT_CHOICES)
    page_size = forms.ChoiceField(required=False, label="Per page", choices=PAGE_SIZE_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["q"].widget.attrs["placeholder"] = "Name or email"

class DashboardFilterForm(BootstrapFormMixin, forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=False, empty_label="All courses")
    date_from = forms.DateField(required=False, label="Enrolled from", widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, label="Enrolled to", widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("date_from"), cleaned.get("date_to")
        if start and end and start > end:
            raise forms.ValidationError("The start date must be on or before the end date.")
        return cleaned