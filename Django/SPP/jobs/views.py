from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Job
from .forms import JobForm
from recruiters.models import RecruiterProfile

from django.db.models import Q

# =====================================
# Student Job Listing
# =====================================

@login_required
def job_list(request):

    jobs = Job.objects.filter(
        status="Open"
    ).order_by("-created_at")

    search = request.GET.get("search")
    job_type = request.GET.get("job_type")
    experience = request.GET.get("experience")
    location = request.GET.get("location")

    if search:

        jobs = jobs.filter(

            Q(job_title__icontains=search) |
            Q(location__icontains=search) |
            Q(qualification__icontains=search)

        )

    if job_type:

        jobs = jobs.filter(
            job_type=job_type
        )

    if experience:

        jobs = jobs.filter(
            experience=experience
        )

    if location:

        jobs = jobs.filter(
            location__icontains=location
        )

    context = {

        "jobs": jobs,

        "job_types": Job.JOB_TYPE_CHOICES,

        "experiences": Job.EXPERIENCE_CHOICES,

    }

    return render(
        request,
        "jobs/job_list.html",
        context
    )

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

            # Trigger notifications to all Students and Placement Officers
            from accounts.models import User
            from accounts.utils import create_notification

            students_and_officers = User.objects.filter(role__in=['student', 'officer'])
            for user in students_and_officers:
                create_notification(
                    user=user,
                    title="New Job Opportunity",
                    message=f"New Job Posted: {job.job_title} at {job.company.company_name}",
                    notification_type="job",
                    link=f"/jobs/{job.id}/"
                )

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