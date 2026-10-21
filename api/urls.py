from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("students", views.StudentViewSet)
router.register("courses", views.CourseViewSet)

urlpatterns = [
    path("token/", obtain_auth_token, name="api_token"),
    path("", include(router.urls)),
]