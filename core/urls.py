
from django.urls import path
from . import views, course_views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("contact/", views.contact, name="contact"),
    path("privacy-policy/", views.privacy_policy, name="privacy"),
    path("students/", views.student_list, name="student_list"),
    path("students/add/", views.student_create, name="student_create"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),
    path("students/<int:pk>/edit/", views.student_update, name="student_update"),
    path("students/<int:pk>/delete/", views.student_delete, name="student_delete"),
    path("students/documents/<str:name>", views.student_document, name="student_document"),
    path("courses/", course_views.CourseList.as_view(), name="course_list"),
    path("courses/add/", course_views.CourseCreate.as_view(), name="course_create"),
    path("courses/<int:pk>/", course_views.CourseDetail.as_view(), name="course_detail"),
    path("courses/<int:pk>/edit/", course_views.CourseUpdate.as_view(), name="course_update"),
    path("courses/<int:pk>/delete/", course_views.CourseDelete.as_view(), name="course_delete"),
    path("instructors/", course_views.InstructorList.as_view(), name="instructor_list"),
    path("instructors/add/", course_views.InstructorCreate.as_view(), name="instructor_create"),
    path("instructors/<int:pk>/edit/", course_views.InstructorUpdate.as_view(), name="instructor_update"),
    path("instructors/<int:pk>/delete/", course_views.InstructorDelete.as_view(), name="instructor_delete"),
    path("dashboard/", views.dashboard, name="dashboard"),
]