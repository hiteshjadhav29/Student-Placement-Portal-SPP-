from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = (
        "job_title",
        "company",
        "job_type",
        "location",
        "salary",
        "vacancies",
        "status",
        "application_deadline",
    )

    list_filter = (
        "status",
        "job_type",
        "experience",
        "location",
    )

    search_fields = (
        "job_title",
        "company__company_name",
        "location",
        "qualification",
    )

    ordering = (
        "-created_at",
    )