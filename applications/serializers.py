from rest_framework import serializers
from .models import JobApplication


class JobApplicationSerializer(serializers.ModelSerializer):
    days_since_applied = serializers.ReadOnlyField()
    needs_follow_up = serializers.ReadOnlyField()

    class Meta:
        model = JobApplication
        fields = [
            'id', 'company', 'role', 'status', 'resume_version', 'job_url',
            'notes', 'date_applied', 'last_updated', 'follow_up_sent',
            'days_since_applied', 'needs_follow_up',
        ]
        read_only_fields = ['id', 'last_updated']