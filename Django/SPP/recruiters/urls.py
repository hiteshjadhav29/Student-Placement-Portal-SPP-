

from django.urls import path
from . import views

app_name = "recruiters"

urlpatterns = [

    path(
        "dashboard/",
        views.recruiter_dashboard,
        name="recruiter_dashboard"
    ),

    path(
        "complete-profile/",
        views.complete_recruiter_profile,
        name="complete_profile"
    ),

    path(
        "profile/",
        views.recruiter_profile,
        name="profile"
    ),

    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile"
    ),

    path(
        "company/",
        views.company_profile,
        name="company_profile"
    ),

    path(
        "company/edit/",
        views.edit_company,
        name="edit_company"
    ),
]