import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from .forms import UserRegistrationForm, LoginForm
from .models import PasswordResetOTP
from students.models import Notification

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


# ==========================
# Forgot Password
# ==========================
def forgot_password(request):
    if request.user.is_authenticated:
        return redirect("accounts:login_redirect")

    if request.method == "POST":
        email_or_username = request.POST.get("email_or_username", "").strip()

        user = User.objects.filter(
            Q(email__iexact=email_or_username) | Q(username__iexact=email_or_username)
        ).first()

        if user:
            from .utils import generate_otp, send_otp_email
            otp = generate_otp()
            PasswordResetOTP.objects.create(user=user, otp=otp)
            try:
                send_otp_email(user, otp)
            except Exception as e:
                messages.warning(request, "Failed to send email. Check SMTP settings.")

            request.session['reset_user_id'] = user.id
            request.session['reset_email'] = user.email
            messages.success(request, f"A 6-digit OTP has been sent to {user.email}.")
            return redirect("accounts:verify_otp")
        else:
            messages.error(request, "No account found with that email or username.")

    return render(request, "accounts/forgot_password.html")


# ==========================
# Verify OTP
# ==========================
def verify_otp(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, "Session expired. Please request OTP again.")
        return redirect("accounts:forgot_password")

    user = get_object_or_404(User, id=user_id)
    email = request.session.get('reset_email', user.email)

    if request.method == "POST":
        otp_code = request.POST.get("otp_code", "").strip()

        otp_record = PasswordResetOTP.objects.filter(
            user=user,
            is_used=False
        ).order_by('-created_at').first()

        if otp_record and otp_record.otp == otp_code and otp_record.is_valid():
            otp_record.is_used = True
            otp_record.save()
            request.session['otp_verified'] = True
            messages.success(request, "OTP verified successfully! Enter your new password.")
            return redirect("accounts:reset_password")
        else:
            messages.error(request, "Invalid or expired OTP. Please try again.")

    return render(request, "accounts/verify_otp.html", {"email": email})


# ==========================
# Reset Password
# ==========================
def reset_password(request):
    user_id = request.session.get('reset_user_id')
    otp_verified = request.session.get('otp_verified')

    if not (user_id and otp_verified):
        messages.error(request, "Unauthorized access. Please start password reset process.")
        return redirect("accounts:forgot_password")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        p1 = request.POST.get("password1")
        p2 = request.POST.get("password2")

        if p1 and p2 and p1 == p2:
            user.set_password(p1)
            user.save()
            request.session.pop('reset_user_id', None)
            request.session.pop('reset_email', None)
            request.session.pop('otp_verified', None)
            messages.success(request, "Password reset successfully! You can now log in.")
            return redirect("accounts:login")
        else:
            messages.error(request, "Passwords do not match or are invalid.")

    return render(request, "accounts/reset_password.html")


# ==========================
# Notifications
# ==========================
@login_required
def notifications(request):
    from .models import UserNotification
    user_notifications = UserNotification.objects.filter(user=request.user)

    return render(
        request,
        "accounts/notifications.html",
        {
            "notifications": user_notifications
        }
    )


@login_required
def mark_notification_read(request, notification_id):
    from .models import UserNotification
    noti = get_object_or_404(UserNotification, id=notification_id, user=request.user)
    noti.is_read = True
    noti.save()
    messages.success(request, "Notification marked as read.")
    return redirect("accounts:notifications")


@login_required
def mark_all_notifications_read(request):
    from .models import UserNotification
    UserNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect("accounts:notifications")


# ==========================
# Account Settings
# ==========================
@login_required
def settings_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_profile":
            request.user.first_name = request.POST.get("first_name", "").strip()
            request.user.last_name = request.POST.get("last_name", "").strip()
            request.user.email = request.POST.get("email", "").strip()
            request.user.phone = request.POST.get("phone", "").strip()
            request.user.save()
            messages.success(request, "Profile settings updated successfully.")

        elif action == "change_password":
            old_pass = request.POST.get("old_password")
            new_pass1 = request.POST.get("new_password1")
            new_pass2 = request.POST.get("new_password2")

            if not request.user.check_password(old_pass):
                messages.error(request, "Current password is incorrect.")
            elif new_pass1 != new_pass2:
                messages.error(request, "New passwords do not match.")
            elif len(new_pass1) < 6:
                messages.error(request, "Password must be at least 6 characters long.")
            else:
                request.user.set_password(new_pass1)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password updated successfully.")

        return redirect("accounts:settings")

    return render(request, "accounts/settings.html")