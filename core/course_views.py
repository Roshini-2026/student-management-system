from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CourseForm, InstructorForm
from .models import Course, Instructor


class CancelLinkMixin:
    """Gives the form and delete pages a Cancel link back to the list."""

    def get_context_data(self, **kwargs):
        return super().get_context_data(cancel_url=self.success_url, **kwargs)


class SavePage(PermissionRequiredMixin, SuccessMessageMixin, CancelLinkMixin):
    """Shared by create and edit pages: permission check, shared template, success message."""
    template_name = "catalog/form.html"

    def get_success_message(self, cleaned_data):
        return f"{self.object} was saved."


class DeletePage(PermissionRequiredMixin, CancelLinkMixin, DeleteView):
    """Shared delete page. If the database refuses (PROTECT), show a message instead of crashing."""
    template_name = "catalog/confirm_delete.html"
    protected_message = "This item is in use and cannot be deleted."

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, self.protected_message)
            return redirect(self.success_url)
        messages.success(self.request, f"{self.object} was deleted.")
        return response


# ---- Courses ----
class CourseList(PermissionRequiredMixin, ListView):
    permission_required = "core.view_course"
    template_name = "catalog/course_list.html"
    context_object_name = "courses"
    # Count in the database, and load all instructors in one extra query (not one per course)
    queryset = Course.objects.annotate(student_count=Count("students")).prefetch_related("instructors").order_by("name")


class CourseDetail(PermissionRequiredMixin, DetailView):
    permission_required = "core.view_course"
    template_name = "catalog/course_detail.html"
    queryset = Course.objects.prefetch_related("instructors")

    def get_context_data(self, **kwargs):
        return super().get_context_data(students=self.object.students.all(), **kwargs)


class CourseCreate(SavePage, CreateView):
    permission_required = "core.add_course"
    model = Course
    form_class = CourseForm
    success_url = reverse_lazy("course_list")
    extra_context = {"noun": "course"}


class CourseUpdate(SavePage, UpdateView):
    permission_required = "core.change_course"
    model = Course
    form_class = CourseForm
    success_url = reverse_lazy("course_list")
    extra_context = {"noun": "course"}


class CourseDelete(DeletePage):
    permission_required = "core.delete_course"
    model = Course
    success_url = reverse_lazy("course_list")
    extra_context = {"noun": "course"}
    protected_message = "This course has enrolled students, so it cannot be deleted."


# ---- Instructors ----
class InstructorList(PermissionRequiredMixin, ListView):
    permission_required = "core.view_instructor"
    template_name = "catalog/instructor_list.html"
    context_object_name = "instructors"
    queryset = Instructor.objects.prefetch_related("courses")


class InstructorCreate(SavePage, CreateView):
    permission_required = "core.add_instructor"
    model = Instructor
    form_class = InstructorForm
    success_url = reverse_lazy("instructor_list")
    extra_context = {"noun": "instructor"}


class InstructorUpdate(SavePage, UpdateView):
    permission_required = "core.change_instructor"
    model = Instructor
    form_class = InstructorForm
    success_url = reverse_lazy("instructor_list")
    extra_context = {"noun": "instructor"}


class InstructorDelete(DeletePage):
    permission_required = "core.delete_instructor"
    model = Instructor
    success_url = reverse_lazy("instructor_list")
    extra_context = {"noun": "instructor"}