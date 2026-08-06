from django import forms
from django.utils import timezone
from .models import Job
from students.models import Student

BRANCH_CHOICES_WITH_ALL = [('ALL', 'All Branches')] + Student.BRANCH_CHOICES


class JobForm(forms.ModelForm):

    target_branches_list = forms.MultipleChoiceField(
        choices=BRANCH_CHOICES_WITH_ALL,
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-check-input'}
        ),
        required=True,
        initial=['ALL'],
        label="Target Branches"
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.target_branches:
                self.fields['target_branches_list'].initial = (
                    self.instance.get_target_branches_list()
                )

    def clean_vacancies(self):
        vacancies = self.cleaned_data.get("vacancies")

        if vacancies and vacancies < 1:
            raise forms.ValidationError("Vacancies must be at least 1.")

        return vacancies

    def clean_salary(self):
        salary = self.cleaned_data.get("salary")

        if not salary or not salary.strip():
            raise forms.ValidationError("Salary cannot be empty.")

        return salary

    def clean_required_skills(self):
        skills = self.cleaned_data.get("required_skills")

        if not skills or len(skills.strip()) < 5:
            raise forms.ValidationError("Please enter valid required skills.")

        return skills

    def clean_application_deadline(self):
        deadline = self.cleaned_data.get("application_deadline")

        if deadline and deadline < timezone.now().date():
            raise forms.ValidationError(
                "Application deadline cannot be in the past."
            )

        return deadline

    def save(self, commit=True):
        instance = super().save(commit=False)

        selected_branches = self.cleaned_data.get(
            "target_branches_list",
            ["ALL"]
        )

        if "ALL" in selected_branches:
            instance.target_branches = "ALL"
        else:
            instance.target_branches = ",".join(selected_branches)

        if commit:
            instance.save()

        return instance