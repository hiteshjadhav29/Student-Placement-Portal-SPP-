from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Password"
        })
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm Password"
        })
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
        ]

        widgets = {

            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Username"
            }),

            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "First Name"
            }),

            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Last Name"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email Address"
            }),

            "role": forms.Select(attrs={
                "class": "form-select"
            }),

        }

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Username already exists."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Email already exists."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Username"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password"
        })
    )


class ForgotPasswordForm(forms.Form):
    identity = forms.CharField(
        label="Username or Registered Email",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your Username or Email address"
        })
    )

    def clean_identity(self):
        identity = self.cleaned_data.get("identity", "").strip()
        user = User.objects.filter(models.Q(username=identity) | models.Q(email__iexact=identity)).first()
        if not user:
            raise forms.ValidationError("No account found with the provided username or email address.")
        if not user.email:
            raise forms.ValidationError("No registered email address found for this account. Contact system admin.")
        self.found_user = user
        return identity


class VerifyOTPForm(forms.Form):
    otp = forms.CharField(
        label="Enter 6-Digit OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            "class": "form-control text-center fs-4 letter-spacing-2",
            "placeholder": "123456",
            "autocomplete": "off"
        })
    )

    def clean_otp(self):
        otp = self.cleaned_data.get("otp", "").strip()
        if not otp.isdigit():
            raise forms.ValidationError("OTP must consist of 6 numeric digits.")
        return otp


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter new password (min 8 characters)"
        })
    )
    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm new password"
        })
    )

    def clean_new_password(self):
        password = self.cleaned_data.get("new_password")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password")
        p2 = cleaned_data.get("confirm_password")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class SettingsProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "10-digit phone number"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if phone:
            digits_only = "".join(filter(str.isdigit, phone))
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise forms.ValidationError("Phone number must contain between 10 and 15 digits.")
        return phone


class ChangePasswordSettingsForm(forms.Form):
    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Current password"})
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "New password (min 8 chars)"})
    )
    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm new password"})
    )

    def clean_new_password(self):
        password = self.cleaned_data.get("new_password")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password")
        p2 = cleaned_data.get("confirm_password")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("New passwords do not match.")
        return cleaned_data