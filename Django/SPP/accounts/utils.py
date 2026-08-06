import random
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetOTP, UserNotification


def generate_otp():
    """Generates a random 6-digit numeric string OTP."""
    return str(random.randint(100000, 999999))


def send_otp_email(user, otp):
    """Sends OTP code to user's registered email address."""
    subject = "Password Reset OTP - Student Placement Portal"
    message = (
        f"Hello {user.username},\n\n"
        f"You requested a password reset for your Student Placement Portal account.\n"
        f"Your 6-digit One-Time Password (OTP) is: {otp}\n\n"
        f"This OTP is valid for 15 minutes. If you did not request this, please ignore this email.\n\n"
        f"Regards,\nStudent Placement Portal Team"
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@spp.com')
    recipient_list = [user.email]
    
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )


def create_notification(user, title, message, notification_type='info', link=None):
    """Creates a UserNotification record for a given user."""
    return UserNotification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link
    )
