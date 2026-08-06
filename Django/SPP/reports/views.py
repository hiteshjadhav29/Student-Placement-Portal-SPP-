from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from students.models import Student
from recruiters.models import RecruiterProfile, Company
from jobs.models import Job
from applications.models import Application
from django.db.models import Count,Q
from django.db.models.functions import TruncMonth
from accounts.decorators import placement_officer_required
import json

@login_required
@placement_officer_required
def dashboard(request):

    total_students = Student.objects.count()

    total_recruiters = RecruiterProfile.objects.count()

    total_jobs = Job.objects.count()

    total_applications = Application.objects.count()

    selected_students = Application.objects.filter(
        status="Selected"
    ).count()

    pending = Application.objects.filter(
        status="Pending"
    ).count()

    rejected = Application.objects.filter(
        status="Rejected"
    ).count()

    placement_percentage = 0

    if total_students:

        placement_percentage = round(

            (selected_students / total_students) * 100,

            2,

        )
        status_data = (
        Application.objects
        .values("status")
        .annotate(total=Count("id"))
    )

    status_labels = [item["status"] for item in status_data]
    status_counts = [item["total"] for item in status_data]

    context = {

        "total_students": total_students,

        "total_recruiters": total_recruiters,

        "total_jobs": total_jobs,

        "total_applications": total_applications,

        "selected_students": selected_students,

        "pending": pending,

        "rejected": rejected,

        "placement_percentage": placement_percentage,

        "status_labels": json.dumps(status_labels),

        "status_counts": json.dumps(status_counts),


    }

    return render(
        request,
        "reports/dashboard.html",
        context,
    )
@login_required
@placement_officer_required
def placement_statistics(request):

    total_students = Student.objects.count()

    total_applications = Application.objects.count()

    selected = Application.objects.filter(
        status="Selected"
    ).count()

    rejected = Application.objects.filter(
        status="Rejected"
    ).count()

    pending = Application.objects.filter(
        status="Pending"
    ).count()

    placement_percentage = 0

    if total_students:

        placement_percentage = round(
            (selected / total_students) * 100,
            2
        )

    context = {

        "total_students": total_students,

        "total_applications": total_applications,

        "selected": selected,

        "rejected": rejected,

        "pending": pending,

        "placement_percentage": placement_percentage,

    }

    return render(
        request,
        "reports/placement_statistics.html",
        context,
    )



@login_required
@placement_officer_required
def company_report(request):

    companies = Company.objects.annotate(

        jobs_posted=Count(
            "jobs",
            distinct=True
        ),

        total_applications=Count(
            "jobs__applications",
            distinct=True
        ),

        selected_students=Count(
            "jobs__applications",
            filter=Q(
                jobs__applications__status="Selected"
            ),
            distinct=True,
        )

    ).order_by("company_name")

    context = {
        "companies": companies,
    }

    return render(
        request,
        "reports/company_report.html",
        context,
    )

@login_required
@placement_officer_required
def branch_report(request):

    branches = []

    students = Student.objects.values(
        "branch"
    ).annotate(
        total_students=Count("id")
    )

    for item in students:

        branch = item["branch"]

        total_students = item["total_students"]

        selected_students = Application.objects.filter(
            student__branch=branch,
            status="Selected"
        ).values(
            "student"
        ).distinct().count()

        placement_percentage = 0

        if total_students > 0:

            placement_percentage = round(
                (selected_students / total_students) * 100,
                2
            )

        branches.append({

            "branch": dict(Student.BRANCH_CHOICES).get(
                branch,
                branch
            ),

            "total_students": total_students,

            "selected_students": selected_students,

            "placement_percentage": placement_percentage,

        })

    context = {

    "branches": branches,

    "branch_labels": json.dumps(
        [b["branch"] for b in branches]
    ),

    "branch_data": json.dumps(
        [b["selected_students"] for b in branches]
    ),

}

    return render(
        request,
        "reports/branch_report.html",
        context,
    )


@login_required
@placement_officer_required
def monthly_report(request):

    monthly_data = (
        Application.objects
        .annotate(month=TruncMonth("applied_at"))
        .values("month")
        .annotate(

            total_applications=Count("id"),

            selected_students=Count(
                "id",
                filter=Q(status="Selected")
            ),

        )
        .order_by("month")
    )

    context = {

        "monthly_data": monthly_data,

    }

    return render(
        request,
        "reports/monthly_report.html",
        context,
    )