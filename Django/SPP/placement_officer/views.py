from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from recruiters.models import Company, RecruiterProfile
from accounts.decorators import placement_officer_required

from students.models import (
    Student,
    Resume,
    Skill,
    Project,
    Certification,
)

from recruiters.models import RecruiterProfile
from jobs.models import Job
from applications.models import Application


@login_required
# @placement_officer_required
def dashboard(request):

    total_students = Student.objects.count()

    total_recruiters = RecruiterProfile.objects.count()

    total_jobs = Job.objects.count()

    total_applications = Application.objects.count()

    open_jobs = Job.objects.filter(
        status="Open"
    ).count()

    selected_students = Application.objects.filter(
        status="Selected"
    ).count()

    context = {

        "total_students": total_students,

        "total_recruiters": total_recruiters,

        "total_jobs": total_jobs,

        "total_applications": total_applications,

        "open_jobs": open_jobs,

        "selected_students": selected_students,

    }

    return render(
        request,
        "placement_officer/dashboard.html",
        context
    )
@login_required
@placement_officer_required
def manage_students(request):

    students = Student.objects.select_related(
        "user",
        "resume"
    ).order_by(
        "roll_number"
    )

    context = {
        "students": students,
    }

    return render(
        request,
        "placement_officer/manage_students.html",
        context,
    )
@login_required
@placement_officer_required
def student_profile(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id
    )

    resume = Resume.objects.filter(
        student=student
    ).first()

    skills = Skill.objects.filter(
        student=student
    )

    projects = Project.objects.filter(
        student=student
    )

    certifications = Certification.objects.filter(
        student=student
    )

    context = {
        "student": student,
        "resume": resume,
        "skills": skills,
        "projects": projects,
        "certifications": certifications,
    }

    return render(
        request,
        "placement_officer/student_profile.html",
        context,
    )
@login_required
@placement_officer_required
def manage_recruiters(request):

    query = request.GET.get("q")

    recruiters = RecruiterProfile.objects.select_related(
        "user",
        "company"
    )

    if query:

        recruiters = recruiters.filter(

            Q(full_name__icontains=query) |
            Q(user__email__icontains=query) |
            Q(company__company_name__icontains=query) |
            Q(designation__icontains=query)

        )

    recruiters = recruiters.order_by("full_name")

    context = {
        "recruiters": recruiters,
        "query": query,
    }

    return render(
        request,
        "placement_officer/manage_recruiters.html",
        context,
    )
@login_required
@placement_officer_required
def recruiter_profile(request, recruiter_id):

    recruiter = get_object_or_404(
        RecruiterProfile,
        id=recruiter_id
    )

    jobs = Job.objects.filter(
        company=recruiter.company
    )

    context = {
        "recruiter": recruiter,
        "jobs": jobs,
    }

    return render(
        request,
        "placement_officer/recruiter_profile.html",
        context,
    )
@login_required
@placement_officer_required
def manage_jobs(request):

    query = request.GET.get("q")

    jobs = Job.objects.select_related(
        "company",
        "recruiter"
    )

    if query:

        jobs = jobs.filter(

            Q(job_title__icontains=query) |
            Q(company__company_name__icontains=query) |
            Q(location__icontains=query) |
            Q(job_type__icontains=query) |
            Q(status__icontains=query)

        )

    jobs = jobs.order_by("-created_at")

    context = {
        "jobs": jobs,
        "query": query,
    }

    return render(
        request,
        "placement_officer/manage_jobs.html",
        context,
    )


@login_required
@placement_officer_required
def job_detail(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    context = {
        "job": job,
    }

    return render(
        request,
        "placement_officer/job_detail.html",
        context,
    )
@login_required
@placement_officer_required
def manage_applications(request):

    query = request.GET.get("q")

    applications = Application.objects.select_related(
        "student__user",
        "job",
        "job__company"
    )

    if query:

        applications = applications.filter(

            Q(student__user__first_name__icontains=query) |
            Q(student__user__last_name__icontains=query) |
            Q(job__job_title__icontains=query) |
            Q(job__company__company_name__icontains=query) |
            Q(status__icontains=query)

        )

    applications = applications.order_by("-applied_at")

    context = {
        "applications": applications,
        "query": query,
    }

    return render(
        request,
        "placement_officer/manage_applications.html",
        context,
    )


@login_required
@placement_officer_required
def application_detail(request, application_id):

    application = get_object_or_404(
        Application,
        id=application_id
    )

    context = {
        "application": application,
    }

    return render(
        request,
        "placement_officer/application_detail.html",
        context,
    )
@login_required
@placement_officer_required
def manage_students(request):

    query = request.GET.get("q")

    students = Student.objects.select_related(
        "user",
        "resume"
    )

    if query:

        students = students.filter(

            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(roll_number__icontains=query) |
            Q(branch__icontains=query)

        )

    students = students.order_by("roll_number")

    context = {

        "students": students,
        "query": query,

    }

    return render(
        request,
        "placement_officer/manage_students.html",
        context,
    )