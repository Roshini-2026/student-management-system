from django.core.validators import MinValueValidator
from django.db import models


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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        permissions = [("view_reports", "Can view reports")]

    def __str__(self):
        return f"{self.full_name} ({self.email})"