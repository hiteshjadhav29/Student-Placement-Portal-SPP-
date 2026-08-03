from django.db import models
from django.conf import settings

from students.models import Student
from jobs.models import Job


class Application(models.Model):

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Under Review", "Under Review"),
        ("Shortlisted", "Shortlisted"),
        ("Rejected", "Rejected"),
        ("Selected", "Selected"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-applied_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["student", "job"],
                name="unique_job_application"
            )
        ]

    def __str__(self):
        return f"{self.student.user.username} - {self.job.job_title}"