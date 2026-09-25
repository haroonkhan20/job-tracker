"""
tasks.py
--------
Background work that runs OUTSIDE the request/response cycle. A web request
finishes fast (just renders a page); this task runs independently, on its
own schedule, checking every application for ones that need a follow-up.
"""

import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def scan_for_follow_ups():
    from .models import JobApplication

    candidates = JobApplication.objects.filter(status='applied', follow_up_sent=False)
    reminded = []

    for application in candidates:
        if application.needs_follow_up:
            logger.info(
                "FOLLOW-UP REMINDER: %s applied to %s (%s) %s days ago, no response yet.",
                application.user.username, application.company, application.role,
                application.days_since_applied,
            )
            reminded.append(application.id)

    return {"checked": candidates.count(), "reminded": reminded, "run_at": str(timezone.now())}