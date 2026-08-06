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


# ==========================
# Forgot Password - Request OTP
# ==========================
def forgot_password(request):
    if request.user.is_authenticated:
        return redirect("accounts:login_redirect")

    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            user = form.found_user
            otp_code = generate_otp()
            # Invalidate any old unused OTPs for this user
            PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)
            
            PasswordResetOTP.objects.create(
                user=user,
                otp=otp_code
            )

            try:
                send_otp_email(user, otp_code)
                request.session['reset_user_id'] = user.id
                messages.success(
                    request,
                    f"An OTP has been sent to your registered email ({user.email}). Please enter it below."
                )
                return redirect("accounts:verify_otp")
            except Exception as e:
                messages.error(request, f"Failed to send email OTP: {str(e)}")
    else:
        form = ForgotPasswordForm()

    return render(request, "accounts/forgot_password.html", {"form": form})


# ==========================
# Verify OTP
# ==========================
def verify_otp(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, "Session expired. Please request a new OTP.")
        return redirect("accounts:forgot_password")

    user = User.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, "User not found.")
        return redirect("accounts:forgot_password")

    if request.method == "POST":
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data["otp"]
            otp_record = PasswordResetOTP.objects.filter(
                user=user,
                otp=otp_input,
                is_used=False
            ).first()

            if otp_record and otp_record.is_valid():
                otp_record.is_used = True
                otp_record.save()
                request.session['otp_verified_user_id'] = user.id
                messages.success(request, "OTP verified successfully! Now set your new password.")
                return redirect("accounts:reset_password")
            else:
                messages.error(request, "Invalid or expired OTP. Please try again or request a new one.")
    else:
        form = VerifyOTPForm()

    return render(
        request,
        "accounts/verify_otp.html",
        {"form": form, "user_email": user.email}
    )


# ==========================
# Reset Password
# ==========================
def reset_password(request):
    user_id = request.session.get('otp_verified_user_id')
    if not user_id:
        messages.error(request, "Unauthorized access. Please verify OTP first.")
        return redirect("accounts:forgot_password")

    user = User.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, "User not found.")
        return redirect("accounts:forgot_password")

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            user.set_password(new_password)
            user.save()
            
            # Clear reset session keys
            request.session.pop('reset_user_id', None)
            request.session.pop('otp_verified_user_id', None)

            # Send notification
            create_notification(
                user=user,
                title="Password Reset Successful",
                message="Your password was reset successfully.",
                notification_type="system"
            )

            messages.success(request, "Your password has been reset successfully! Please log in with your new password.")
            return redirect("accounts:login")
    else:
        form = ResetPasswordForm()

    return render(request, "accounts/reset_password.html", {"form": form})


# ==========================
# Settings View (All Roles)
# ==========================
from django.contrib.auth.decorators import login_required
from .forms import ForgotPasswordForm, VerifyOTPForm, ResetPasswordForm, SettingsProfileForm, ChangePasswordSettingsForm
from .models import PasswordResetOTP, UserNotification
from .utils import generate_otp, send_otp_email, create_notification


@login_required
def settings_view(request):
    profile_form = SettingsProfileForm(instance=request.user)
    password_form = ChangePasswordSettingsForm()

    if request.method == "POST":
        if "update_profile" in request.POST:
            profile_form = SettingsProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile details updated successfully!")
                return redirect("accounts:settings")

        elif "change_password" in request.POST:
            password_form = ChangePasswordSettingsForm(request.POST)
            if password_form.is_valid():
                current_pw = password_form.cleaned_data["current_password"]
                if not request.user.check_password(current_pw):
                    messages.error(request, "Incorrect current password.")
                else:
                    new_pw = password_form.cleaned_data["new_password"]
                    request.user.set_password(new_pw)
                    request.user.save()
                    # Re-authenticate session after password change
                    login(request, request.user)
                    messages.success(request, "Your password has been changed successfully!")
                    create_notification(
                        user=request.user,
                        title="Password Changed",
                        message="Your account password was changed from settings.",
                        notification_type="system"
                    )
                    return redirect("accounts:settings")

    return render(
        request,
        "accounts/settings.html",
        {
            "profile_form": profile_form,
            "password_form": password_form,
        }
    )


# ==========================
# Notifications List View
# ==========================
@login_required
def notifications_view(request):
    notifications = UserNotification.objects.filter(user=request.user)
    return render(
        request,
        "accounts/notifications.html",
        {"notifications": notifications}
    )


# ==========================
# Mark Single Notification Read
# ==========================
@login_required
def mark_notification_read(request, notification_id):
    notification = UserNotification.objects.filter(id=notification_id, user=request.user).first()
    if notification:
        notification.is_read = True
        notification.save()
        if notification.link:
            return redirect(notification.link)
    return redirect("accounts:notifications")


# ==========================
# Mark All Notifications Read
# ==========================
@login_required
def mark_all_notifications_read(request):
    UserNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect("accounts:notifications")