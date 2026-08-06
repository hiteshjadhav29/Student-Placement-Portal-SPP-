from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "redirect/",
        views.login_redirect,
        name="login_redirect"
    ),

    path(
        "forgot-password/",
        views.forgot_password,
        name="forgot_password",
    ),

    path(
        "verify-otp/",
        views.verify_otp,
        name="verify_otp",
    ),

    path(
        "reset-password/",
        views.reset_password,
        name="reset_password",
    ),

    path(
        "notifications/",
        views.notifications,
        name="notifications",
    ),

    path(
        "notifications/<int:notification_id>/read/",
        views.mark_notification_read,
        name="mark_notification_read",
    ),

    path(
        "notifications/read-all/",
        views.mark_all_notifications_read,
        name="mark_all_notifications_read",
    ),

    path(
        "settings/",
        views.settings_view,
        name="settings",
    ),
]