
import re

from django import forms


class ContactForm(forms.Form):
    full_name = forms.CharField(max_length=100, label="Full name")
    email = forms.EmailField(label="Email address")
    phone = forms.CharField(max_length=20, required=False, label="Phone number")
    subject = forms.CharField(max_length=150, label="Subject")
    message = forms.CharField(
        max_length=2000,
        label="Message",
        widget=forms.Textarea(attrs={"rows": 5}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_class = "form-control"
            if self.is_bound and name in self.errors:
                css_class += " is-invalid"
            field.widget.attrs["class"] = css_class

    def clean_phone(self):
        phone = self.cleaned_data["phone"].replace(" ", "").replace("-", "")
        if phone and not re.fullmatch(r"\+?\d{7,15}", phone):
            raise forms.ValidationError(
                "Enter a valid phone number, for example +919876543210."
            )
        return phone