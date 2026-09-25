"""
test_models.py
---------------
Tests the JobApplication model's business logic directly -- no HTTP requests,
no views, just the model's own methods. Fast, and isolates "is this specific
calculation correct" from "does the whole request/response cycle work."
"""

import pytest
from datetime import date, timedelta
from django.contrib.auth.models import User
from applications.models import JobApplication


@pytest.mark.django_db
def test_days_since_applied_calculates_correctly():
    user = User.objects.create_user('testuser', password='pass123')
    app = JobApplication.objects.create(
        user=user, company="TestCo", role="Engineer",
        date_applied=date.today() - timedelta(days=10),
    )
    assert app.days_since_applied == 10


@pytest.mark.django_db
def test_needs_follow_up_true_after_14_days_with_no_response():
    user = User.objects.create_user('testuser2', password='pass123')
    app = JobApplication.objects.create(
        user=user, company="TestCo", role="Engineer", status='applied',
        date_applied=date.today() - timedelta(days=15), follow_up_sent=False,
    )
    assert app.needs_follow_up is True


@pytest.mark.django_db
def test_needs_follow_up_false_if_already_sent():
    user = User.objects.create_user('testuser3', password='pass123')
    app = JobApplication.objects.create(
        user=user, company="TestCo", role="Engineer", status='applied',
        date_applied=date.today() - timedelta(days=20), follow_up_sent=True,
    )
    assert app.needs_follow_up is False


@pytest.mark.django_db
def test_needs_follow_up_false_if_status_changed():
    user = User.objects.create_user('testuser4', password='pass123')
    app = JobApplication.objects.create(
        user=user, company="TestCo", role="Engineer", status='interview',
        date_applied=date.today() - timedelta(days=20),
    )
    assert app.needs_follow_up is False