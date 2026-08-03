from django.urls import path
from . import views

app_name = "applications"

urlpatterns = [

    path(
        "",
        views.my_applications,
        name="my_applications"
    ),

    path(
        "apply/<int:job_id>/",
        views.apply_job,
        name="apply_job"
    ),

    path(
        "recruiter/",
        views.recruiter_applications,
        name="recruiter_applications"
    ),

    path(
        "detail/<int:application_id>/",
        views.application_detail,
        name="application_detail"
    ),

    path(
        "update/<int:application_id>/",
        views.update_status,
        name="update_status"
    ),
]