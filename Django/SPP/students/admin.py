from django.contrib import admin
from .models import (
    Student,
    Resume,
    Skill,
    Project,
    Certification,
    Notification,
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "roll_number",
        "user",
        "branch",
        "semester",
        "cgpa",
    )

    search_fields = (
        "roll_number",
        "user__username",
        "user__first_name",
        "user__last_name",
    )

    list_filter = (
        "branch",
        "semester",
        "gender",
    )


admin.site.register(Resume)
admin.site.register(Skill)
admin.site.register(Project)
admin.site.register(Certification)
admin.site.register(Notification)   