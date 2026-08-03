from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [

    # ==========================
    # Student
    # ==========================

    path(
        "",
        views.job_list,
        name="job_list"
    ),

    path(
        "<int:job_id>/",
        views.job_detail,
        name="job_detail"
    ),

    # ==========================
    # Recruiter
    # ==========================

    path(
        "add/",
        views.add_job,
        name="add_job"
    ),

    path(
        "manage/",
        views.manage_jobs,
        name="manage_jobs"
    ),

    path(
        "<int:job_id>/edit/",
        views.edit_job,
        name="edit_job"
    ),

    path(
        "<int:job_id>/delete/",
        views.delete_job,
        name="delete_job"
    ),

]