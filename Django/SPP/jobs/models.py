from django.db import models
from django.conf import settings
from recruiters.models import Company


class Job(models.Model):

    JOB_TYPE_CHOICES = (
        ('Full-Time', 'Full-Time'),
        ('Part-Time', 'Part-Time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
    )

    EXPERIENCE_CHOICES = (
        ('Fresher', 'Fresher'),
        ('0-1 Years', '0-1 Years'),
        ('1-3 Years', '1-3 Years'),
        ('3-5 Years', '3-5 Years'),
        ('5+ Years', '5+ Years'),
    )

    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('Closed', 'Closed'),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs'
    )

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_jobs'
    )

    job_title = models.CharField(max_length=150)

    job_description = models.TextField()

    required_skills = models.TextField(
        help_text="Separate skills using commas"
    )

    qualification = models.CharField(max_length=150)

    experience = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='Fresher'
    )

    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES
    )

    location = models.CharField(max_length=150)

    salary = models.CharField(max_length=100)

    vacancies = models.PositiveIntegerField(default=1)

    application_deadline = models.DateField()

    target_branches = models.CharField(
        max_length=255,
        default='ALL',
        help_text="Target branches for job posting (e.g. CO,IT,AIML or ALL)"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Open'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def get_target_branches_list(self):
        if not self.target_branches or self.target_branches == 'ALL':
            return ['ALL']
        return [b.strip() for b in self.target_branches.split(',') if b.strip()]

    def __str__(self):
        return f"{self.job_title} - {self.company.company_name}"