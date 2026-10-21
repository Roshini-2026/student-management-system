from django.db.models import Count
from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response

from core.models import Course, Student

from .serializers import CourseSerializer, StudentSerializer


class ModelPermissions(DjangoModelPermissions):
    """Same rules as the website. By default reading needs no permission, so we require 'view' too."""
    perms_map = {
        **DjangoModelPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
    }


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related("course")
    serializer_class = StudentSerializer
    permission_classes = [ModelPermissions]
    filterset_fields = ["course", "gender", "enrollment_status", "is_active"]
    search_fields = ["full_name", "email"]
    ordering_fields = ["full_name", "created_at"]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.annotate(student_count=Count("students")).prefetch_related("instructors").order_by("name")
    serializer_class = CourseSerializer
    permission_classes = [ModelPermissions]
    filterset_fields = ["status"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "fee"]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "This course has enrolled students, so it cannot be deleted."},
                status=status.HTTP_409_CONFLICT,
            )