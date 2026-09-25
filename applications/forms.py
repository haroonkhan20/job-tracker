from django import forms
from .models import JobApplication, Resume


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['company', 'role', 'status', 'resume_version', 'job_url', 'notes', 'date_applied']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 12, 'cols': 80}),
            'date_applied': forms.DateInput(attrs={'type': 'date'}),
        }


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['name', 'content']
        widgets = {'content': forms.Textarea(attrs={'rows': 20, 'cols': 80})}


