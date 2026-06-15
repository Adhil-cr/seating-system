"""
URL configuration for core project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/students/", include("students.urls")),
    path("api/exams/", include("exams.urls")),
    path("api/halls/", include("halls.urls")),
    path("api/seating/", include("seating.urls")),

    path("", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("dashboard/", views.dashboard_page, name="dashboard"),
    path("students/upload/", views.upload_students_page, name="students_upload"),
    path("exams/config/", views.exam_config_page, name="exam_config"),
    path("seating/generate/", views.seating_generate_page, name="seating_generate"),
    path("seating/view/", views.seating_view_page, name="seating_view"),
    path("profile/", views.profile_page, name="profile"),
]

if settings.STANDALONE:
    urlpatterns += [
        re_path(
            r"^static/(?P<path>.*)$",
            serve,
            {"document_root": str(settings.STANDALONE_STATIC_DIR)},
        ),
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": str(settings.MEDIA_ROOT)},
        ),
    ]
elif settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_SOURCE_DIR,
    )
