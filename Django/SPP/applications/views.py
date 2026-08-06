
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from jobs.models import Job
from students.models import Student
from recruiters.models import RecruiterProfile
from .models import Application


# =====================================
# Apply for Job
# =====================================

@login_required
def apply_job(request, job_id):

    if request.user.role != "student":
        messages.error(
            request,
            "Only students can apply for jobs."
        )
        return redirect("jobs:job_list")

    student = get_object_or_404(
        Student,
        user=request.user
    )

    job = get_object_or_404(
        Job,
        id=job_id,
        status="Open"
    )

    # Deadline constraint check
    from django.utils import timezone
    if job.application_deadline < timezone.now().date():
        messages.error(
            request,
            "The application deadline for this job has passed."
        )
        return redirect("jobs:job_list")

    # Prevent duplicate applications
    if Application.objects.filter(
        student=student,
        job=job
    ).exists():

        messages.warning(
            request,
            "You have already applied for this job."
        )

        return redirect("applications:my_applications")

    if request.method == "POST":

        app_obj = Application.objects.create(
            student=student,
            job=job,
            status="Pending"
        )

        # Trigger Notification to Recruiter & Student
        from accounts.utils import create_notification
        create_notification(
            user=student.user,
            title="Application Submitted",
            message=f"You successfully applied for {job.job_title} at {job.company.company_name}.",
            notification_type="application",
            link="/applications/my-applications/"
        )
        if job.recruiter:
            create_notification(
                user=job.recruiter,
                title="New Applicant",
                message=f"Student {student.user.get_full_name() or student.user.username} applied for {job.job_title}.",
                notification_type="application",
                link=f"/applications/recruiter/"
            )

        messages.success(
            request,
            "Application submitted successfully."
        )

        return redirect("applications:my_applications")

    return render(
        request,
        "applications/apply_job.html",
        {
            "job": job
        }
    )
# =====================================
# Student Applications
# =====================================


@login_required
def my_applications(request):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    applications = Application.objects.filter(
        student=student
    ).select_related(
        "job",
        "job__company"
    )

    return render(
        request,
        "applications/my_applications.html",
        {
            "applications": applications,
        }
    )



@login_required
def application_detail(request, application_id):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    application = get_object_or_404(
        Application,
        id=application_id,
        student=student
    )

    return render(
        request,
        "applications/application_detail.html",
        {
            "application": application,
        }
    )


# =====================================
# Recruiter Applications
# =====================================

@login_required
def recruiter_applications(request):

    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    applications = Application.objects.filter(
        job__company=recruiter.company
    ).select_related(
        "student",
        "job"
    )

    return render(
        request,
        "applications/recruiter_applications.html",
        {
            "applications": applications
        }
    )


# =====================================
# Update Status
# =====================================

@login_required
def update_status(request, application_id):

    application = get_object_or_404(
        Application,
        id=application_id
    )

    if request.method == "POST":

        new_status = request.POST.get("status")
        application.status = new_status
        application.save()

        # Trigger notification to student & officers
        from accounts.models import User
        from accounts.utils import create_notification

        create_notification(
            user=application.student.user,
            title="Application Status Updated",
            message=f"Your application status for {application.job.job_title} has been updated to '{new_status}'.",
            notification_type="application",
            link="/applications/my-applications/"
        )

        officers = User.objects.filter(role="officer")
        for officer in officers:
            create_notification(
                user=officer,
                title="Application Status Update",
                message=f"Application for {application.student.user.username} on {application.job.job_title} changed to '{new_status}'.",
                notification_type="application"
            )

        messages.success(
            request,
            "Application status updated successfully."
        )

        return redirect(
            "applications:recruiter_applications"
        )

    return render(
        request,
        "applications/update_status.html",
        {
            "application": application,
            "status_choices": Application.STATUS_CHOICES,
        }
    )