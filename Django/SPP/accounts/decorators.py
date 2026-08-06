from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page.")
            return redirect("accounts:login")
        if request.user.role != "student":
            messages.error(request, "Access denied. Student permissions required.")
            return redirect("accounts:login_redirect")
        return view_func(request, *args, **kwargs)
    return wrapper


def recruiter_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page.")
            return redirect("accounts:login")
        if request.user.role != "recruiter":
            messages.error(request, "Access denied. Recruiter permissions required.")
            return redirect("accounts:login_redirect")
        return view_func(request, *args, **kwargs)
    return wrapper


def placement_officer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page.")
            return redirect("accounts:login")
        if request.user.role != "officer":
            messages.error(request, "Access denied. Placement Officer permissions required.")
            return redirect("accounts:login_redirect")
        return view_func(request, *args, **kwargs)
    return wrapper