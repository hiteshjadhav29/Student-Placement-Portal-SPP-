from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import PasswordResetOTP, UserNotification

User = get_user_model()


class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="teststudent",
            email="teststudent@example.com",
            password="Password123",
            role="student"
        )

    def test_login_success(self):
        response = self.client.post(reverse("accounts:login"), {
            "username": "teststudent",
            "password": "Password123"
        })
        self.assertEqual(response.status_code, 302)

    def test_forgot_password_flow(self):
        # Request OTP
        response = self.client.post(reverse("accounts:forgot_password"), {
            "email_or_username": "teststudent@example.com"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:verify_otp"))

        # Verify OTP created
        otp_obj = PasswordResetOTP.objects.filter(user=self.user).first()
        self.assertIsNotNone(otp_obj)

        # Post invalid OTP
        response_invalid = self.client.post(reverse("accounts:verify_otp"), {
            "otp_code": "000000"
        })
        self.assertEqual(response_invalid.status_code, 200)

        # Post valid OTP
        response_valid = self.client.post(reverse("accounts:verify_otp"), {
            "otp_code": otp_obj.otp
        })
        self.assertEqual(response_valid.status_code, 302)
        self.assertRedirects(response_valid, reverse("accounts:reset_password"))

        # Reset password
        response_reset = self.client.post(reverse("accounts:reset_password"), {
            "password1": "NewPassword123",
            "password2": "NewPassword123"
        })
        self.assertEqual(response_reset.status_code, 302)
        self.assertRedirects(response_reset, reverse("accounts:login"))

        # Try login with new password
        self.assertTrue(self.client.login(username="teststudent", password="NewPassword123"))

