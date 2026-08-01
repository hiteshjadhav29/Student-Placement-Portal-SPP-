from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm

User = get_user_model()


def register(request):

    if request.method == "POST":

        form = UserRegistrationForm(request.POST, request.FILES)

        if form.is_valid():

            user = form.save(commit=False)

            user.set_password(form.cleaned_data["password1"])

            user.save()

            messages.success(
                request,
                "Account created successfully."
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


def login_view(request):

    if request.user.is_authenticated:

        if request.user.role == "student":
            return redirect("students:dashboard")

        elif request.user.role == "recruiter":
            return redirect("recruiters:recruiter_dashboard")

        elif request.user.role == "officer":
            return redirect("officers:dashboard")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                username=username,
                password=password
            )

            if user:

                login(request, user)

                if user.role == "student":
                    return redirect("students:dashboard")

                elif user.role == "recruiter":
                    return redirect("recruiters:recruiter_dashboard")

                elif user.role == "officer":
                    return redirect("officers:dashboard")

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )


def logout_view(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect("accounts:login")