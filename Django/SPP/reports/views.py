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


# ==========================================
# Report Export to CSV & Email to Officer
# ==========================================
import csv
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.contrib import messages
from accounts.utils import create_notification


def _generate_report_csv_buffer(report_type):
    """Internal helper to generate CSV string content based on report_type."""
    import io
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == "placement-stats":
        total_students = Student.objects.count()
        total_applications = Application.objects.count()
        selected = Application.objects.filter(status="Selected").count()
        rejected = Application.objects.filter(status="Rejected").count()
        pending = Application.objects.filter(status="Pending").count()
        placement_percentage = round((selected / total_students * 100), 2) if total_students else 0

        writer.writerow(["Metric", "Count / Value"])
        writer.writerow(["Total Registered Students", total_students])
        writer.writerow(["Total Job Applications", total_applications])
        writer.writerow(["Selected Students", selected])
        writer.writerow(["Pending Applications", pending])
        writer.writerow(["Rejected Applications", rejected])
        writer.writerow(["Overall Placement Percentage", f"{placement_percentage}%"])

    elif report_type == "company-report":
        companies = Company.objects.annotate(
            jobs_posted=Count("jobs", distinct=True),
            total_applications=Count("jobs__applications", distinct=True),
            selected_students=Count("jobs__applications", filter=Q(jobs__applications__status="Selected"), distinct=True),
        ).order_by("company_name")

        writer.writerow(["Company Name", "Industry", "Location", "Jobs Posted", "Total Applications Received", "Selected Students"])
        for comp in companies:
            writer.writerow([
                comp.company_name,
                comp.industry,
                comp.location,
                comp.jobs_posted,
                comp.total_applications,
                comp.selected_students
            ])

    elif report_type == "branch-report":
        students = Student.objects.values("branch").annotate(total_students=Count("id"))
        writer.writerow(["Branch Code", "Branch Name", "Total Students", "Selected Students", "Placement Percentage"])
        for item in students:
            b_code = item["branch"]
            b_name = dict(Student.BRANCH_CHOICES).get(b_code, b_code)
            tot_st = item["total_students"]
            sel_st = Application.objects.filter(student__branch=b_code, status="Selected").values("student").distinct().count()
            pct = round((sel_st / tot_st * 100), 2) if tot_st > 0 else 0
            writer.writerow([b_code, b_name, tot_st, sel_st, f"{pct}%"])

    elif report_type == "monthly-report":
        monthly_data = (
            Application.objects
            .annotate(month=TruncMonth("applied_at"))
            .values("month")
            .annotate(
                total_applications=Count("id"),
                selected_students=Count("id", filter=Q(status="Selected")),
            )
            .order_by("month")
        )
        writer.writerow(["Month", "Total Applications", "Selected Students"])
        for row in monthly_data:
            m_str = row["month"].strftime("%B %Y") if row["month"] else "N/A"
            writer.writerow([m_str, row["total_applications"], row["selected_students"]])

    else:
        # Default full application summary
        applications = Application.objects.select_related("student__user", "job__company").all()
        writer.writerow(["Student Roll No", "Student Name", "Branch", "CGPA", "Job Title", "Company Name", "Application Status", "Applied At"])
        for app in applications:
            writer.writerow([
                app.student.roll_number,
                app.student.user.get_full_name() or app.student.user.username,
                app.student.get_branch_display(),
                app.student.cgpa,
                app.job.job_title,
                app.job.company.company_name,
                app.status,
                app.applied_at.strftime("%Y-%m-%d %H:%M")
            ])

    return output.getvalue()


@login_required
@placement_officer_required
def export_report_csv(request, report_type):
    csv_data = _generate_report_csv_buffer(report_type)
    response = HttpResponse(csv_data, content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'
    return response


@login_required
@placement_officer_required
def email_report_to_officer(request, report_type):
    user_email = request.user.email
    if not user_email:
        messages.error(request, "Your officer account does not have a registered email address.")
        return redirect(request.META.get('HTTP_REFERER', 'reports:dashboard'))

    csv_data = _generate_report_csv_buffer(report_type)
    filename = f"{report_type}_report.csv"

    subject = f"Placement Report ({report_type.replace('-', ' ').title()}) - SPP Portal"
    body = (
        f"Hello {request.user.get_full_name() or request.user.username},\n\n"
        f"Attached is the requested placement report ({report_type.replace('-', ' ').title()}) generated from the Placement Portal.\n\n"
        f"Best regards,\nStudent Placement Portal System"
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=None,
        to=[user_email]
    )
    email.attach(filename, csv_data, 'text/csv')

    try:
        email.send()
        messages.success(request, f"Report successfully generated and emailed to {user_email}!")
        create_notification(
            user=request.user,
            title="Report Emailed",
            message=f"The requested report ({report_type}) was sent to {user_email}.",
            notification_type="report"
        )
    except Exception as e:
        messages.error(request, f"Failed to send email: {str(e)}")

    return redirect(request.META.get('HTTP_REFERER', 'reports:dashboard'))