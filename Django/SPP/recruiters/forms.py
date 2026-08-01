from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import Company, RecruiterProfile

User = get_user_model()


# ==========================
# Company Registration Form
# ==========================
class CompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = [
            'company_name',
            'company_email',
            'company_phone',
            'website',
            'industry',
            'location',
            'description',
            'logo'
        ]

        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'company_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# ==========================
# Recruiter Registration Form
# ==========================
class RecruiterRegistrationForm(forms.ModelForm):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = RecruiterProfile

        fields = [
            'full_name',
            'designation',
            'phone',
            'gender',
            'profile_picture'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")

        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']

        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")

        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")

        return phone

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


# ==========================
# Recruiter Login Form
# ==========================
class RecruiterLoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }
        )
    )


# ==========================
# Recruiter Profile Update
# ==========================
class RecruiterProfileForm(forms.ModelForm):

    class Meta:
        model = RecruiterProfile

        fields = [
            'full_name',
            'designation',
            'phone',
            'gender',
            'profile_picture'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }