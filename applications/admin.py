from django.contrib import admin
from .models import JobApplication
from .models import Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['company', 'role', 'status', 'user', 'date_applied', 'follow_up_sent']
    list_filter = ['status', 'follow_up_sent']
    search_fields = ['company', 'role']