
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models

from .files import (
    MaxFileSize,
    document_path,
    get_private_storage,
    photo_path,
    validate_pdf_content,
)


class Instructor(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    specialization = models.CharField(max_length=100)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Course(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    duration_weeks = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    fee = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    instructors = models.ManyToManyField(Instructor, related_name="courses", blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    class EnrollmentStatus(models.TextChoices):
        ENROLLED = "enrolled", "Enrolled"
        COMPLETED = "completed", "Completed"
        DROPPED = "dropped", "Dropped"

    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    date_of_birth = models.DateField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="students")
    enrollment_status = models.CharField(
        max_length=10, choices=EnrollmentStatus.choices, default=EnrollmentStatus.ENROLLED
    )
    address = models.TextField(blank=True)
    profile_photo = models.ImageField(
        upload_to=photo_path, blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png"]), MaxFileSize(2)],
        help_text="JPG or PNG, up to 2 MB.",
    )
    supporting_document = models.FileField(
        upload_to=document_path, storage=get_private_storage, blank=True,
        validators=[FileExtensionValidator(["pdf"]), validate_pdf_content, MaxFileSize(5)],
        help_text="PDF only, up to 5 MB. Visible to Admin and Staff only.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        permissions = [("view_reports", "Can view reports")]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    FILE_FIELDS = ("profile_photo", "supporting_document")

    def save(self, *args, **kwargs):
        """After saving, delete files that were replaced or cleared."""
        old = Student.objects.only(*self.FILE_FIELDS).filter(pk=self.pk).first() if self.pk else None
        super().save(*args, **kwargs)
        for name in self.FILE_FIELDS if old else ():
            old_file = getattr(old, name)
            if old_file and old_file.name != getattr(self, name).name:
                old_file.delete(save=False)

 