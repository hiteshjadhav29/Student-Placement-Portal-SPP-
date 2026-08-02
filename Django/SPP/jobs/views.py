from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Job
from .forms import JobForm
from recruiters.models import RecruiterProfile


# ==============================
# Add Job
# ==============================
@login_required
def add_job(request):

    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    if request.method == "POST":

        form = JobForm(request.POST)

        if form.is_valid():

            job = form.save(commit=False)

            job.company = recruiter.company
            job.recruiter = request.user

            job.save()

            messages.success(
                request,
                "Job posted successfully."
            )

            return redirect("jobs:manage_jobs")

    else:

        form = JobForm()

    return render(
        request,
        "jobs/add_job.html",
        {
            "form": form
        }
    )


# ==============================
# Manage Jobs
# ==============================
@login_required
def manage_jobs(request):

    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    jobs = Job.objects.filter(
        company=recruiter.company
    ).order_by("-created_at")

    return render(
        request,
        "jobs/manage_jobs.html",
        {
            "jobs": jobs
        }
    )


# ==============================
# Job Details
# ==============================
@login_required
def job_detail(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    return render(
        request,
        "jobs/job_detail.html",
        {
            "job": job
        }
    )


# ==============================
# Edit Job
# ==============================
@login_required
def edit_job(request, job_id):

    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    job = get_object_or_404(
        Job,
        id=job_id,
        company=recruiter.company
    )

    if request.method == "POST":

        form = JobForm(
            request.POST,
            instance=job
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Job updated successfully."
            )

            return redirect("jobs:manage_jobs")

    else:

        form = JobForm(instance=job)

    return render(
        request,
        "jobs/edit_job.html",
        {
            "form": form,
            "job": job
        }
    )


# ==============================
# Delete Job
# ==============================
@login_required
def delete_job(request, job_id):

    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    job = get_object_or_404(
        Job,
        id=job_id,
        company=recruiter.company
    )

    if request.method == "POST":

        job.delete()

        messages.success(
            request,
            "Job deleted successfully."
        )

        return redirect("jobs:manage_jobs")

    return render(
        request,
        "jobs/delete_job.html",
        {
            "job": job
        }
    )