import re

from django import forms

from .models import Student

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
    """Adds Bootstrap classes to every field (red border if it has an error)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(widget, forms.Select):
                css_class = "form-select"
            else:
                css_class = "form-control"
            if self.is_bound and name in self.errors:
                css_class += " is-invalid"
            widget.attrs["class"] = css_class
            if name in ("phone", "mobile_number"):
                widget.attrs.update(PHONE_ATTRS)


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
            "full_name", "email", "mobile_number", "gender",
            "date_of_birth", "course", "address", "is_active",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_mobile_number(self):
        return clean_phone_number(self.cleaned_data["mobile_number"])

def get_course_choices():
        """Course dropdown options, read from the database when the form is validated or shown."""
        courses = Student.objects.order_by("course").values_list("course", flat=True).distinct()
        return [("", "All courses")] + [(course, course) for course in courses]

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