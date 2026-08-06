from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "placement-statistics/",
        views.placement_statistics,
        name="placement_statistics",
    ),

    path(
        "company-report/",
        views.company_report,
        name="company_report",
    ),

    path(
        "branch-report/",
        views.branch_report,
        name="branch_report",
    ),

    path(
        "monthly-report/",
        views.monthly_report,
        name="monthly_report",
    ),

]