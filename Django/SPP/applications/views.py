
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

        Application.objects.create(
            student=student,
            job=job,
            status="Pending"
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

    from django.shortcuts import render, get_object_or_404
    from django.contrib.auth.decorators import login_required

    from .models import Application
    from students.models import Student


@login_required
def application_detail(request, application_id):


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
            "applications": applications
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
# Application Details
# =====================================

@login_required
def application_detail(request, application_id):

    application = get_object_or_404(
        Application,
        id=application_id
    )

    return render(
        request,
        "applications/application_detail.html",
        {
            "application": application
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

        application.status = request.POST.get("status")
        application.save()

        messages.success(
            request,
            "Application status updated successfully."
        )

        return redirect(
            "applications:application_detail",
            application.id
        )

    return render(
        request,
        "applications/update_status.html",
        {
            "application": application,
            "status_choices": Application.STATUS_CHOICES
        }
    )
    application = get_object_or_404(
        Application,
        id=application_id,
        student=student
    )

    context = {
        "application": application,
    }

    return render(
        request,
        "applications/application_detail.html",
        context

    )