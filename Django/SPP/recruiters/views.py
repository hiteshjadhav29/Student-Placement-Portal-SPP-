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
def register(request):

    if request.method == "POST":

        company_form = CompanyForm(request.POST, request.FILES)
        recruiter_form = RecruiterRegistrationForm(request.POST, request.FILES)

        if company_form.is_valid() and recruiter_form.is_valid():

            company = company_form.save()

            user = User.objects.create_user(
                username=recruiter_form.cleaned_data["username"],
                email=recruiter_form.cleaned_data["email"],
                password=recruiter_form.cleaned_data["password1"],
                role="recruiter"
            )

            recruiter = recruiter_form.save(commit=False)
            recruiter.user = user
            recruiter.company = company
            recruiter.save()

            messages.success(request, "Recruiter registered successfully.")

            return redirect("recruiter_login")

    else:
        company_form = CompanyForm()
        recruiter_form = RecruiterRegistrationForm()

    context = {
        "company_form": company_form,
        "recruiter_form": recruiter_form,
    }

    return render(request, "recruiters/register.html", context)


# =====================================
# Login
# =====================================
def recruiter_login(request):

    if request.user.is_authenticated:
        return redirect("recruiter_dashboard")

    form = RecruiterLoginForm(request, data=request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(
                username=username,
                password=password
            )

            if user is not None:

                if user.role != "recruiter":
                    messages.error(
                        request,
                        "Only recruiters can login here."
                    )
                    return redirect("recruiter_login")

                login(request, user)

                return redirect("recruiter_dashboard")

    return render(
        request,
        "recruiters/login.html",
        {"form": form}
    )


# =====================================
# Dashboard
# =====================================
@login_required
def recruiter_dashboard(request):

    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    context = {
        "recruiter": recruiter,
        "company": recruiter.company,
    }

    return render(
        request,
        "recruiters/dashboard.html",
        context
    )


# =====================================
# Recruiter Profile
# =====================================
@login_required
def recruiter_profile(request):

    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

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

    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

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

            return redirect("recruiter_profile")

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
@login_required
def recruiter_logout(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect("recruiter_login")