from django import forms
from .models import (
    Student,
    Resume,
    Skill,
    Project,
    Certification,
)

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student

        fields = [
            "roll_number",
            "phone",
            "branch",
            "semester",
            "cgpa",
            "date_of_birth",
            "gender",
            "address",
            "profile_photo",
            "github_url",
            "linkedin_url",
        ]
class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume

        fields = [
            "resume_file",
        ]

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill

        fields = [
            "skill_name",
        ]
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project

        fields = [
            "title",
            "description",
            "technology",
            "github_link",
        ]
class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification

        fields = [
            "certificate_name",
            "issued_by",
            "issue_date",
            "certificate_file",    
        ]