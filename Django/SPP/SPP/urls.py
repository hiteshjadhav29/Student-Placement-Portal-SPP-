from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from . import views

urlpatterns = [

    path("", views.home, name="home"),

    path("admin/", admin.site.urls),

    path("", include("accounts.urls")),

    path("students/", include("students.urls")),
    path("student/<path:subpath>", RedirectView.as_view(url="/students/%(subpath)s", permanent=False)),
    path("student/", RedirectView.as_view(url="/students/dashboard/", permanent=False)),

    path("recruiter/", include("recruiters.urls")),
    path("recruiters/<path:subpath>", RedirectView.as_view(url="/recruiter/%(subpath)s", permanent=False)),
    path("recruiters/", RedirectView.as_view(url="/recruiter/dashboard/", permanent=False)),

    path("jobs/", include("jobs.urls")),

    path(
        "applications/",
        include(("applications.urls", "applications"), namespace="applications"),
    ),
    path("interview/", include("interview.urls")),

    path(
        "placement-officer/",
        include("placement_officer.urls"),
    ),
    path(
        "reports/",
        include("reports.urls"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)