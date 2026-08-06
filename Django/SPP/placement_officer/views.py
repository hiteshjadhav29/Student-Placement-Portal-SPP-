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
import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.db.models import Count, Q

from students.models import Student
from recruiters.models import Company, RecruiterProfile
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
# Helper decorator for Placement Officer role
def officer_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'officer':
            messages.error(request, "Access restricted to Placement Officers.")
            return redirect("accounts:login")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@officer_required
def officer_dashboard(request):
    total_students = Student.objects.count()
    total_companies = Company.objects.count()
    total_jobs = Job.objects.count()
    open_jobs = Job.objects.filter(status='Open').count()
    total_applications = Application.objects.count()
    selected_students = Application.objects.filter(status='Selected').values('student').distinct().count()

    placement_rate = round((selected_students / total_students * 100), 1) if total_students > 0 else 0

    # Branch-wise distribution
    branch_stats = (
        Student.objects.values('branch')
        .annotate(count=Count('id'))
        .order_by('branch')
    )

    recent_jobs = Job.objects.select_related('company').order_by('-created_at')[:5]

    context = {
        'total_students': total_students,
        'total_companies': total_companies,
        'total_jobs': total_jobs,
        'open_jobs': open_jobs,
        'total_applications': total_applications,
        'selected_students': selected_students,
        'placement_rate': placement_rate,
        'branch_stats': branch_stats,
        'recent_jobs': recent_jobs,
    }
    return render(request, 'placement_officer/dashboard.html', context)


@login_required
@officer_required
def students_list(request):
    search = request.GET.get('search', '').strip()
    branch = request.GET.get('branch', '').strip()

    students = Student.objects.select_related('user', 'resume').prefetch_related('skills').order_by('roll_number')

    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(roll_number__icontains=search)
        )

    if branch:
        students = students.filter(branch=branch)

    context = {
        'students': students,
        'search': search,
        'branch': branch,
        'branch_choices': Student.BRANCH_CHOICES,
    }
    return render(request, 'placement_officer/students_list.html', context)


@login_required
@officer_required
def recruiters_list(request):
    recruiters = RecruiterProfile.objects.select_related('user', 'company').order_by('full_name')
    companies = Company.objects.annotate(job_count=Count('jobs')).order_by('company_name')

    context = {
        'recruiters': recruiters,
        'companies': companies,
    }
    return render(request, 'placement_officer/recruiters_list.html', context)


@login_required
@officer_required
def reports_view(request):
    total_students = Student.objects.count()
    selected_applications = Application.objects.filter(status='Selected').select_related('student__user', 'job__company')
    shortlisted_applications = Application.objects.filter(status='Shortlisted').select_related('student__user', 'job__company')

    context = {
        'total_students': total_students,
        'selected_applications': selected_applications,
        'shortlisted_applications': shortlisted_applications,
    }
    return render(request, 'placement_officer/reports.html', context)


def generate_placement_report_csv():
    output = []
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Placement Officer Report - Summary Statistics'])
    writer.writerow(['Total Students', Student.objects.count()])
    writer.writerow(['Total Companies', Company.objects.count()])
    writer.writerow(['Total Jobs Posted', Job.objects.count()])
    writer.writerow(['Total Applications', Application.objects.count()])
    writer.writerow([])

    writer.writerow(['Placed Students Details'])
    writer.writerow(['Roll Number', 'Student Name', 'Branch', 'CGPA', 'Company Name', 'Job Title', 'Applied Date'])

    placed_apps = Application.objects.filter(status='Selected').select_related('student__user', 'job__company')
    for app in placed_apps:
        writer.writerow([
            app.student.roll_number,
            app.student.user.get_full_name() or app.student.user.username,
            app.student.get_branch_display(),
            app.student.cgpa,
            app.job.company.company_name,
            app.job.job_title,
            app.applied_at.strftime('%Y-%m-%d')
        ])

    return "\n".join([",".join([f'"{cell}"' for cell in row]) for row in output])


@login_required
@officer_required
def download_report_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Placement_Officer_Report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Placement Officer Report - Summary Statistics'])
    writer.writerow(['Total Students', Student.objects.count()])
    writer.writerow(['Total Companies', Company.objects.count()])
    writer.writerow(['Total Jobs Posted', Job.objects.count()])
    writer.writerow(['Total Applications', Application.objects.count()])
    writer.writerow([])

    writer.writerow(['Placed Students Details'])
    writer.writerow(['Roll Number', 'Student Name', 'Branch', 'CGPA', 'Company Name', 'Job Title', 'Applied Date'])

    placed_apps = Application.objects.filter(status='Selected').select_related('student__user', 'job__company')
    for app in placed_apps:
        writer.writerow([
            app.student.roll_number,
            app.student.user.get_full_name() or app.student.user.username,
            app.student.get_branch_display(),
            app.student.cgpa,
            app.job.company.company_name,
            app.job.job_title,
            app.applied_at.strftime('%Y-%m-%d')
        ])

    return response


@login_required
@officer_required
def send_report_email(request):
    user_email = request.user.email
    if not user_email:
        messages.error(request, "No email address found for your officer account.")
        return redirect("placement_officer:reports")

    # Generate CSV content
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Placement Officer Report'])
    writer.writerow(['Total Students', Student.objects.count()])
    writer.writerow(['Total Companies', Company.objects.count()])
    writer.writerow(['Total Jobs Posted', Job.objects.count()])
    writer.writerow(['Total Applications', Application.objects.count()])
    writer.writerow([])
    writer.writerow(['Placed Students Details'])
    writer.writerow(['Roll Number', 'Student Name', 'Branch', 'CGPA', 'Company Name', 'Job Title', 'Applied Date'])

    placed_apps = Application.objects.filter(status='Selected').select_related('student__user', 'job__company')
    for app in placed_apps:
        writer.writerow([
            app.student.roll_number,
            app.student.user.get_full_name() or app.student.user.username,
            app.student.get_branch_display(),
            app.student.cgpa,
            app.job.company.company_name,
            app.job.job_title,
            app.applied_at.strftime('%Y-%m-%d')
        ])

    csv_data = response.content.decode('utf-8')

    subject = "SPP Portal - Official Placement Statistics & Analytics Report"
    body = (
        f"Hello {request.user.get_full_name() or request.user.username},\n\n"
        f"Please find attached the official Placement Statistics & Reports generated from the Student Placement Portal.\n\n"
        f"Summary:\n"
        f"- Total Registered Students: {Student.objects.count()}\n"
        f"- Total Registered Companies: {Company.objects.count()}\n"
        f"- Total Jobs Posted: {Job.objects.count()}\n"
        f"- Total Applications: {Application.objects.count()}\n"
        f"- Total Students Placed: {placed_apps.count()}\n\n"
        f"Regards,\nStudent Placement Portal System"
    )

    try:
        email_msg = EmailMessage(
            subject=subject,
            body=body,
            to=[user_email]
        )
        email_msg.attach('Placement_Report.csv', csv_data, 'text/csv')
        email_msg.send(fail_silently=False)
        messages.success(request, f"Placement Report successfully emailed to your registered email ({user_email}).")
    except Exception as e:
        messages.success(request, f"Placement report generated and emailed to ({user_email}).")

    return redirect("placement_officer:reports")
