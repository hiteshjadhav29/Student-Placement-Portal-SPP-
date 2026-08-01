from django import forms
from .models import Job


class JobForm(forms.ModelForm):

    class Meta:
        model = Job

        fields = [
            'job_title',
            'job_description',
            'required_skills',
            'qualification',
            'experience',
            'job_type',
            'location',
            'salary',
            'vacancies',
            'application_deadline',
            'status',
        ]

        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Job Title'
            }),

            'job_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter Job Description'
            }),

            'required_skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Python, Django, MySQL, HTML, CSS'
            }),

            'qualification': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'B.E, B.Tech, Diploma, MCA...'
            }),

            'experience': forms.Select(attrs={
                'class': 'form-select'
            }),

            'job_type': forms.Select(attrs={
                'class': 'form-select'
            }),

            'location': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'salary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. ₹6 LPA'
            }),

            'vacancies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),

            'application_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def clean_vacancies(self):
        vacancies = self.cleaned_data.get("vacancies")

        if vacancies < 1:
            raise forms.ValidationError(
                "Vacancies must be at least 1."
            )

        return vacancies

    def clean_salary(self):
        salary = self.cleaned_data.get("salary")

        if not salary:
            raise forms.ValidationError(
                "Salary cannot be empty."
            )

        return salary

    def clean_required_skills(self):
        skills = self.cleaned_data.get("required_skills")

        if len(skills.strip()) < 5:
            raise forms.ValidationError(
                "Please enter valid skills."
            )

        return skills