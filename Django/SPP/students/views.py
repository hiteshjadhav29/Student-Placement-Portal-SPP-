from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import (
    Student,
    Resume,
    Skill,
    Project,
    Certification,
    Notification,
)

from .forms import (
    StudentForm,
    ResumeForm,
    SkillForm,
    ProjectForm,
    CertificationForm,
)


@login_required
def dashboard(request):

    if request.user.role != "student":
        return redirect("accounts:login")

    if not Student.objects.filter(user=request.user).exists():
        return redirect("students:complete_profile")

    student = Student.objects.get(user=request.user)

    try:
        resume = student.resume
    except Resume.DoesNotExist:
        resume = None

    context = {
        "student": student,
        "resume": resume,
        "skills_count": student.skills.count(),
        "projects_count": student.projects.count(),
        "certifications_count": student.certifications.count(),
    }

    return render(
        request,
        "student/dashboard.html",
        context
    )
@login_required
def profile(request):
    student = get_object_or_404(Student, user=request.user)

    context = {
        "student": student,
    }

    return render(request, "student/profile.html", context)

@login_required
def edit_profile(request):
    student = get_object_or_404(Student, user=request.user)

    if request.method == "POST":
        form = StudentForm(
            request.POST,
            request.FILES,
            instance=student
        )

        if form.is_valid():
            form.save()
            return redirect("students:profile")

    else:
        form = StudentForm(instance=student)

    return render(
        request,
        "student/edit_profile.html",
        {
            "form": form,
        }
    )

@login_required
def resume(request):
    student = get_object_or_404(Student, user=request.user)

    try:
        resume = student.resume
    except Resume.DoesNotExist:
        resume = None

    context = {
        "resume": resume,
    }

    return render(request, "student/resume.html", context)

@login_required
def upload_resume(request):
    student = get_object_or_404(Student, user=request.user)

    try:
        resume = student.resume
    except Resume.DoesNotExist:
        resume = None

    if request.method == "POST":
        form = ResumeForm(
            request.POST,
            request.FILES,
            instance=resume
        )

        if form.is_valid():
            resume = form.save(commit=False)
            resume.student = student
            resume.save()

            return redirect("students:resume")

    else:
        form = ResumeForm(instance=resume)

    context = {
        "form": form,
    }

    return render(request, "student/upload_resume.html", context)
@login_required
def skills(request):
    student = get_object_or_404(Student, user=request.user)

    skills = Skill.objects.filter(student=student)

    return render(
        request,
        "student/skills.html",
        {
            "skills": skills,
        }
    )


@login_required
def add_skill(request):
    student = get_object_or_404(Student, user=request.user)

    if request.method == "POST":
        form = SkillForm(request.POST)

        if form.is_valid():
            skill = form.save(commit=False)
            skill.student = student
            skill.save()

            return redirect("students:skills")

    else:
        form = SkillForm()

    return render(
        request,
        "student/add_skill.html",
        {
            "form": form,
        }
    )
@login_required
def edit_skill(request, skill_id):
    student = get_object_or_404(Student, user=request.user)

    skill = get_object_or_404(
        Skill,
        id=skill_id,
        student=student
    )

    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)

        if form.is_valid():
            form.save()
            return redirect("students:skills")

    else:
        form = SkillForm(instance=skill)

    return render(
        request,
        "student/edit_skill.html",
        {
            "form": form,
        }
    )


@login_required
def delete_skill(request, skill_id):
    student = get_object_or_404(Student, user=request.user)

    skill = get_object_or_404(
        Skill,
        id=skill_id,
        student=student
    )

    if request.method == "POST":
        skill.delete()
        return redirect("students:skills")

    return render(
        request,
        "student/delete_skill.html",
        {
            "skill": skill,
        }
    )
@login_required
def projects(request):
    student = get_object_or_404(Student, user=request.user)

    projects = Project.objects.filter(student=student)

    return render(
        request,
        "student/projects.html",
        {
            "projects": projects,
        }
    )


@login_required
def add_project(request):
    student = get_object_or_404(Student, user=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.student = student
            project.save()

            return redirect("students:projects")

    else:
        form = ProjectForm()

    return render(
        request,
        "student/add_project.html",
        {
            "form": form,
        }
    )


@login_required
def edit_project(request, project_id):
    student = get_object_or_404(Student, user=request.user)

    project = get_object_or_404(
        Project,
        id=project_id,
        student=student
    )

    if request.method == "POST":
        form = ProjectForm(
            request.POST,
            instance=project
        )

        if form.is_valid():
            form.save()
            return redirect("students:projects")

    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "student/edit_project.html",
        {
            "form": form,
        }
    )


@login_required
def delete_project(request, project_id):
    student = get_object_or_404(Student, user=request.user)

    project = get_object_or_404(
        Project,
        id=project_id,
        student=student
    )

    if request.method == "POST":
        project.delete()
        return redirect("students:projects")

    return render(
        request,
        "student/delete_project.html",
        {
            "project": project,
        }
    )

@login_required
def certifications(request):
    student = get_object_or_404(Student, user=request.user)

    certifications = Certification.objects.filter(
        student=student
    )

    return render(
        request,
        "student/certifications.html",
        {
            "certifications": certifications,
        }
    )


@login_required
def add_certification(request):
    student = get_object_or_404(Student, user=request.user)

    if request.method == "POST":
        form = CertificationForm(request.POST)

        if form.is_valid():
            certification = form.save(commit=False)
            certification.student = student
            certification.save()

            return redirect("students:certifications")

    else:
        form = CertificationForm()

    return render(
        request,
        "student/add_certification.html",
        {
            "form": form,
        }
    )


@login_required
def edit_certification(request, certification_id):
    student = get_object_or_404(Student, user=request.user)

    certification = get_object_or_404(
        Certification,
        id=certification_id,
        student=student
    )

    if request.method == "POST":
        form = CertificationForm(
            request.POST,
            request.FILES,
            instance=certification
        )

        if form.is_valid():
            form.save()
            return redirect("students:certifications")

    else:
        form = CertificationForm(instance=certification)

    return render(
        request,
        "student/edit_certification.html",
        {
            "form": form,
        }
    )


@login_required
def delete_certification(request, certification_id):
    student = get_object_or_404(Student, user=request.user)

    certification = get_object_or_404(
        Certification,
        id=certification_id,
        student=student
    )

    if request.method == "POST":
        certification.delete()
        return redirect("students:certifications")

    return render(
        request,
        "student/delete_certification.html",
        {
            "certification": certification,
        }
    )
@login_required
def complete_profile(request):

    if request.user.role != "student":
        return redirect("accounts:login")

    # Already completed
    if Student.objects.filter(user=request.user).exists():
        return redirect("students:dashboard")

    if request.method == "POST":

        form = StudentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            student = form.save(commit=False)
            student.user = request.user
            student.save()

            messages.success(
                request,
                "Student profile created successfully."
            )

            return redirect("students:dashboard")

    else:

        form = StudentForm()

    return render(
        request,
        "student/complete_profile.html",
        {
            "form": form
        }
    )