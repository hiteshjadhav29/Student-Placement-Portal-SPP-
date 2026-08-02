from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator



class Student(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    BRANCH_CHOICES = [
    ('CO', 'Computer Engineering'),
    ('IT', 'Information Technology'),
    ('AIML', 'Artificial Intelligence & Machine Learning'),
    ('ENTC', 'Electronics & Telecommunication'),
    ('ME', 'Mechanical Engineering'),
    ('CEV', 'Civil Engineering'),
]

    SEMESTER_CHOICES = [
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
        (5, 'Semester 5'),
        (6, 'Semester 6'),
    ]

    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="student_profile"
)

    roll_number = models.CharField(
    max_length=20,
    unique=True,
    verbose_name="Roll Number"
)
    phone = models.CharField(max_length=10)

    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)

    cgpa = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(10)
    ]
)

    date_of_birth = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    address = models.TextField()

    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True
    )

    github_url = models.URLField(
        blank=True,
        null=True
    )

    linkedin_url = models.URLField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['roll_number']
        verbose_name = "Student"
        verbose_name_plural = "Students"


    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Resume(models.Model):
    student = models.OneToOneField(
    Student,
    on_delete=models.CASCADE,
    related_name="resume"
)

    resume_file = models.FileField(
        upload_to='resumes/'
    )

    resume_score = models.PositiveIntegerField(
        default=0
    )

    ats_score = models.PositiveIntegerField(
        default=0
    )

    ai_feedback = models.TextField(
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.student.user.username} Resume"

class Skill(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="skills"
    )

    skill_name = models.CharField(max_length=100)

    def __str__(self):
        return self.skill_name

class Project(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="projects"
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    technology = models.CharField(max_length=200)

    github_link = models.URLField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title

class Certification(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="certifications"
    )

    certificate_name = models.CharField(max_length=200)

    issued_by = models.CharField(max_length=200)

    issue_date = models.DateField()

    certificate_file = models.FileField(
    upload_to="certificates/",
    blank=True,
    null=True
)

    def __str__(self):
        return self.certificate_name

class Notification(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
