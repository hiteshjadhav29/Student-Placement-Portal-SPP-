from django.contrib import admin
from .models import Company, RecruiterProfile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = (
        "company_name",
        "company_email",
        "industry",
        "location",
    )

    search_fields = (
        "company_name",
        "industry",
    )


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):

    list_display = (
        "full_name",
        "designation",
        "company",
        "is_verified",
    )

    search_fields = (
        "full_name",
        "designation",
    )

    list_filter = (
        "is_verified",
        "gender",
    )