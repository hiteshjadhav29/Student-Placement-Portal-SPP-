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

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        digits = "".join(filter(str.isdigit, phone))
        if len(digits) < 10 or len(digits) > 15:
            raise forms.ValidationError("Phone number must contain between 10 and 15 digits.")
        return phone

    def clean_cgpa(self):
        cgpa = self.cleaned_data.get("cgpa")
        if cgpa is not None and (cgpa < 0 or cgpa > 10):
            raise forms.ValidationError("CGPA must be between 0.0 and 10.0.")
        return cgpa


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume

        fields = [
            "resume_file",
        ]

    def clean_resume_file(self):
        file = self.cleaned_data.get("resume_file")
        if file:
            # Validate File Size (Max 5 MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume file size cannot exceed 5MB.")
            # Validate Extension
            import os
            ext = os.path.splitext(file.name)[1].lower()
            valid_extensions = ['.pdf', '.doc', '.docx']
            if ext not in valid_extensions:
                raise forms.ValidationError("Unsupported file format. Please upload a PDF or Word document (.pdf, .doc, .docx).")
        return file


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