from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected'),
        ('ghosted', 'No Response'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    resume_version = models.CharField(max_length=100, blank=True)
    job_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    date_applied = models.DateField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    follow_up_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_applied']

    def __str__(self):
        return f"{self.company} — {self.role} ({self.get_status_display()})"

    @property
    def days_since_applied(self):
        return (timezone.now().date() - self.date_applied).days

    @property
    def needs_follow_up(self):
        return (
            self.status == 'applied'
            and not self.follow_up_sent
            and self.days_since_applied >= 14
        )


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    name = models.CharField(max_length=100, help_text="e.g. pydev, C5, Infosys-tailored")
    content = models.TextField(help_text="Paste the full text content of this resume version")

    def __str__(self):
        return self.name