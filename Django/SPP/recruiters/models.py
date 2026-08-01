from django.db import models
from django.conf import settings


class Company(models.Model):
    company_name = models.CharField(max_length=150)
    company_email = models.EmailField(unique=True)
    company_phone = models.CharField(max_length=15)
    website = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['company_name']

    def __str__(self):
        return self.company_name


class RecruiterProfile(models.Model):

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recruiter_profile'
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='recruiters'
    )

    full_name = models.CharField(max_length=150)

    designation = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    profile_picture = models.ImageField(
        upload_to='recruiter_profiles/',
        blank=True,
        null=True
    )

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} - {self.company.company_name}"