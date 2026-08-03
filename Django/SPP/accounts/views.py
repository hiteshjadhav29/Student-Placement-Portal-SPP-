from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm

User = get_user_model()


# ==========================
# Register
# ==========================
def register(request):

    if request.user.is_authenticated:
        return redirect("accounts:login_redirect")

    if request.method == "POST":

        form = UserRegistrationForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.set_password(form.cleaned_data["password1"])

            user.save()

            messages.success(
                request,
                "Registration successful! Please login."
            )

            return redirect("accounts:login")

    else:

        form = UserRegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


# ==========================
# Login
# ==========================
def login_view(request):

    if request.user.is_authenticated:
        return redirect("accounts:login_redirect")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                messages.success(
                    request,
                    f"Welcome {user.username}!"
                )

                return redirect("accounts:login_redirect")

            else:

                messages.error(
                    request,
                    "Invalid username or password."
                )

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )


# ==========================
# Redirect According to Role
# ==========================

def login_redirect(request):

    if not request.user.is_authenticated:
        return redirect("accounts:login")

    if request.user.role == "student":

        from students.models import Student

        if Student.objects.filter(user=request.user).exists():
            return redirect("students:dashboard")

        return redirect("students:complete_profile")

    elif request.user.role == "recruiter":

        from recruiters.models import RecruiterProfile

        # Check if recruiter profile exists
        if RecruiterProfile.objects.filter(user=request.user).exists():
            return redirect("recruiters:recruiter_dashboard")

        # First-time recruiter
        return redirect("recruiters:complete_profile")

    elif request.user.role == "officer":
        return redirect("placement_officer:dashboard")

    else:
        logout(request)

        messages.error(
            request,
            "Invalid account role."
        )

        return redirect("accounts:login")


# ==========================
# Logout
# ==========================
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("accounts:login")