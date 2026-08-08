from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Company, RecruiterProfile
from .forms import (
    CompanyForm,
    RecruiterRegistrationForm,
    RecruiterLoginForm,
    RecruiterProfileForm
)

User = get_user_model()


# =====================================
# Home Page
# =====================================
def home(request):
    return render(request, "recruiters/home.html")


# =====================================
# Recruiter Registration
# =====================================
# def register(request):

#     if request.method == "POST":

#         company_form = CompanyForm(request.POST, request.FILES)
#         recruiter_form = RecruiterRegistrationForm(request.POST, request.FILES)

#         if company_form.is_valid() and recruiter_form.is_valid():

#             company = company_form.save()

#             user = User.objects.create_user(
#                 username=recruiter_form.cleaned_data["username"],
#                 email=recruiter_form.cleaned_data["email"],
#                 password=recruiter_form.cleaned_data["password1"],
#                 role="recruiter"
#             )

#             recruiter = recruiter_form.save(commit=False)
#             recruiter.user = user
#             recruiter.company = company
#             recruiter.save()

#             messages.success(request, "Recruiter registered successfully.")

#             return redirect("recruiter_login")

#     else:
#         company_form = CompanyForm()
#         recruiter_form = RecruiterRegistrationForm()

#     context = {
#         "company_form": company_form,
#         "recruiter_form": recruiter_form,
#     }

#     return render(request, "recruiters/register.html", context)


# # =====================================
# # Login
# # =====================================
# def recruiter_login(request):

#     if request.user.is_authenticated:
#         return redirect("recruiter_dashboard")

#     form = RecruiterLoginForm(request, data=request.POST or None)

#     if request.method == "POST":

#         if form.is_valid():

#             username = form.cleaned_data.get("username")
#             password = form.cleaned_data.get("password")

#             user = authenticate(
#                 username=username,
#                 password=password
#             )

#             if user is not None:

#                 if user.role != "recruiter":
#                     messages.error(
#                         request,
#                         "Only recruiters can login here."
#                     )
#                     return redirect("recruiter_login")

#                 login(request, user)

#                 return redirect("recruiters:recruiter_dashboard")

#     return render(
#         request,
#         "recruiters/login.html",
#         {"form": form}
#     )


# =====================================
# Dashboard
# =====================================
@login_required
def recruiter_dashboard(request):

    # Only recruiters can access
    if request.user.role != "recruiter":
        messages.error(
            request,
            "Access denied."
        )
        return redirect("accounts:login")

    # If recruiter profile is not created yet
    if not RecruiterProfile.objects.filter(user=request.user).exists():
        return redirect("recruiters:complete_profile")

    recruiter = RecruiterProfile.objects.get(user=request.user)
    company = recruiter.company

    from jobs.models import Job
    from applications.models import Application

    jobs_qs = Job.objects.filter(company=company).order_by('-created_at') if company else Job.objects.none()
    total_jobs = jobs_qs.count()
    active_jobs = jobs_qs.filter(status='Open').count()

    apps_qs = Application.objects.filter(job__company=company) if company else Application.objects.none()
    total_applicants = apps_qs.count()
    shortlisted = apps_qs.filter(status='Shortlisted').count()
    selected = apps_qs.filter(status='Selected').count()

    recent_jobs = jobs_qs[:5]
    recent_applications = apps_qs.select_related('student__user', 'job').order_by('-applied_at')[:5]

    context = {
        "recruiter": recruiter,
        "company": company,
        "jobs": recent_jobs,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applicants": total_applicants,
        "shortlisted": shortlisted,
        "selected": selected,
        "recent_applications": recent_applications,
    }

    return render(
        request,
        "recruiters/recruiter_dashboard.html",
        context
    )



# =====================================
# Recruiter Profile
# =====================================
@login_required
def recruiter_profile(request):

    if not RecruiterProfile.objects.filter(user=request.user).exists():
        return redirect("recruiters:complete_profile")

    recruiter = RecruiterProfile.objects.get(user=request.user)

    return render(
        request,
        "recruiters/profile.html",
        {
            "recruiter": recruiter
        }
    )


# =====================================
# Edit Profile
# =====================================
@login_required
def edit_profile(request):

    if not RecruiterProfile.objects.filter(user=request.user).exists():
        return redirect("recruiters:complete_profile")

    recruiter = RecruiterProfile.objects.get(user=request.user)

    if request.method == "POST":

        form = RecruiterProfileForm(
            request.POST,
            request.FILES,
            instance=recruiter
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect("recruiters:profile")

    else:

        form = RecruiterProfileForm(
            instance=recruiter
        )

    return render(
        request,
        "recruiters/edit_profile.html",
        {
            "form": form
        }
    )


# =====================================
# Logout
# =====================================
# @login_required
# def recruiter_logout(request):

#     logout(request)

#     messages.success(
#         request,
#         "Logged out successfully."
#     )

#     return redirect("recruiters:recruiter_login")

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import RecruiterProfile
from .forms import CompanyForm, RecruiterProfileForm


@login_required
def complete_recruiter_profile(request):

    # Only recruiters should access this page
    if request.user.role != "recruiter":
        return redirect("accounts:login")

    # If profile already exists
    if RecruiterProfile.objects.filter(user=request.user).exists():
        return redirect("recruiters:recruiter_dashboard")

    if request.method == "POST":

        company_form = CompanyForm(request.POST, request.FILES)
        recruiter_form = RecruiterProfileForm(request.POST, request.FILES)

        if company_form.is_valid() and recruiter_form.is_valid():

            company = company_form.save()

            recruiter = recruiter_form.save(commit=False)
            recruiter.user = request.user
            recruiter.company = company
            recruiter.save()

            messages.success(
                request,
                "Recruiter profile created successfully."
            )

            return redirect("recruiters:recruiter_dashboard")

    else:

        company_form = CompanyForm()
        recruiter_form = RecruiterProfileForm()

    return render(
        request,
        "recruiters/complete_profile.html",
        {
            "company_form": company_form,
            "recruiter_form": recruiter_form,
        },
    )



@login_required
def company_profile(request):

    recruiter = RecruiterProfile.objects.get(
        user=request.user
    )

    company = recruiter.company

    context = {
        "company": company,
        "recruiter": recruiter,
    }

    return render(
        request,
        "recruiters/company_profile.html",
        context
    )

# =====================================
# Edit Company Profile
# =====================================
@login_required
def edit_company(request):

    if request.user.role != "recruiter":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")

    try:
        recruiter = RecruiterProfile.objects.get(user=request.user)
    except RecruiterProfile.DoesNotExist:
        return redirect("recruiters:complete_profile")

    company = recruiter.company

    if request.method == "POST":

        form = CompanyForm(
            request.POST,
            request.FILES,
            instance=company
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Company profile updated successfully."
            )

            return redirect("recruiters:company_profile")

    else:

        form = CompanyForm(instance=company)

    return render(
        request,
        "recruiters/edit_company.html",
        {
            "form": form
        }
    )