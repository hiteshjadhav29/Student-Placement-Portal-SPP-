from django.urls import path
from . import views

app_name = "placement_officer"

urlpatterns = [

    path(
        "dashboard/",
        views.officer_dashboard,
        name="dashboard",
    ),

    # Students
    path(
        "students/",
        views.manage_students,
        name="manage_students",
    ),

    path(
        "students/<int:student_id>/",
        views.student_profile,
        name="student_profile",
    ),

    # Recruiters
    path(
        "recruiters/",
        views.manage_recruiters,
        name="manage_recruiters",
    ),

    path(
        "recruiters/<int:recruiter_id>/",
        views.recruiter_profile,
        name="recruiter_profile",
    ),

    # Jobs
    path(
        "jobs/",
        views.manage_jobs,
        name="manage_jobs",
    ),

    path(
        "jobs/<int:job_id>/",
        views.job_detail,
        name="job_detail",
    ),

    # Applications
    path(
        "applications/",
        views.manage_applications,
        name="manage_applications",
    ),

    path(
        "applications/<int:application_id>/",
        views.application_detail,
        name="application_detail",
    ),

    # Reports
    path(
        "reports/",
        views.reports_view,
        name="reports",
    ),

    path(
        "reports/download/",
        views.download_report_csv,
        name="download_report",
    ),

    path(
        "reports/email/",
        views.send_report_email,
        name="email_report",
    ),
]