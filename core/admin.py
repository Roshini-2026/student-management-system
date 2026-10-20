from django.contrib import admin
from django.db.models import Count
from django.utils import timezone

from .models import Course, Instructor, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "mobile_number", "course", "enrollment_status", "created_at")
    list_filter = ("course", "gender", "enrollment_status")
    search_fields = ("full_name", "email", "mobile_number")
    list_select_related = ("course",)  # avoids one query per row
    list_per_page = 25
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Personal details", {"fields": ("full_name", "email", "mobile_number", "gender", "date_of_birth", "address")}),
        ("Enrollment", {"fields": ("course", "enrollment_status", "is_active")}),
        ("System information", {"fields": ("created_at", "updated_at")}),
    )
    actions = ["mark_completed"]

    @admin.action(description="Mark selected students as completed")
    def mark_completed(self, request, queryset):
        # update() skips save(), so we refresh updated_at ourselves
        count = queryset.update(
            enrollment_status=Student.EnrollmentStatus.COMPLETED, updated_at=timezone.now()
        )
        self.message_user(request, f"{count} student(s) marked as completed.")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "status", "fee", "duration_weeks", "student_count")
    list_filter = ("status",)
    search_fields = ("name", "code")
    filter_horizontal = ("instructors",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_student_count=Count("students"))

    @admin.display(description="Students", ordering="_student_count")
    def student_count(self, obj):
        return obj._student_count


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "specialization")
    search_fields = ("full_name", "email")