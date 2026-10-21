from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from core.forms import clean_phone_number
from core.models import Course, Student


class StudentSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)
    SENSITIVE_FIELDS = ("mobile_number", "date_of_birth", "address")

    class Meta:
        model = Student
        fields = [
            "id", "full_name", "email", "mobile_number", "gender", "date_of_birth", "course",
            "course_name", "enrollment_status", "address", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_mobile_number(self, value):
        try:
            return clean_phone_number(value)  # the same 10-digit rule as the website
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)

    def validate_course(self, course):
        current = self.instance.course_id if self.instance else None
        if course.status != Course.Status.ACTIVE and course.pk != current:
            raise serializers.ValidationError("Choose an active course.")
        return course

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self.context["request"].user.has_perm("core.change_student"):
            for name in self.SENSITIVE_FIELDS:  # Viewers never see private details
                data.pop(name, None)
        return data


class CourseSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "name", "code", "description", "duration_weeks", "fee", "status", "instructors", "student_count"]

    def get_student_count(self, course):
        # Lists use the database count from the view; single objects count on demand
        return course.student_count if hasattr(course, "student_count") else course.students.count()