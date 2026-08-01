from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [

    # Add Job
    path(
        "add/",
        views.add_job,
        name="add_job"
    ),

    # Manage Jobs
    path(
        "manage/",
        views.manage_jobs,
        name="manage_jobs"
    ),

    # Job Details
    path(
        "<int:job_id>/",
        views.job_detail,
        name="job_detail"
    ),

    # Edit Job
    path(
        "<int:job_id>/edit/",
        views.edit_job,
        name="edit_job"
    ),

    # Delete Job
    path(
        "<int:job_id>/delete/",
        views.delete_job,
        name="delete_job"
    ),

]