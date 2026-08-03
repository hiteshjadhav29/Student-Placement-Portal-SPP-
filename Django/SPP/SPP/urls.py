from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [

    path("", views.home, name="home"),

    path("admin/", admin.site.urls),

    path("", include("accounts.urls")),

    path("student/", include("students.urls")),

    path("recruiter/", include("recruiters.urls")),

    path("jobs/", include("jobs.urls")),

    path(
    "applications/",
    include(("applications.urls", "applications"), namespace="applications"),
),

    ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)