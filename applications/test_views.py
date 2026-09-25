"""
test_views.py
-------------
Tests actual HTTP requests through Django's test client -- this simulates a
real browser hitting your views, without needing a running server. The most
important thing tested here: that one user can NEVER see another user's data.
"""

import pytest
from django.contrib.auth.models import User
from applications.models import JobApplication


@pytest.mark.django_db
def test_application_list_requires_login(client):
    response = client.get('/applications/')
    assert response.status_code == 302  # redirected to login, not shown the page


@pytest.mark.django_db
def test_logged_in_user_sees_their_own_applications(client):
    user = User.objects.create_user('alice', password='pass123')
    JobApplication.objects.create(user=user, company="AliceCo", role="Engineer")

    client.login(username='alice', password='pass123')
    response = client.get('/applications/')

    assert response.status_code == 200
    assert b"AliceCo" in response.content


@pytest.mark.django_db
def test_user_cannot_see_another_users_applications():
    """The single most important test in this app."""
    alice = User.objects.create_user('alice2', password='pass123')
    bob = User.objects.create_user('bob', password='pass123')
    JobApplication.objects.create(user=alice, company="AliceSecret", role="Engineer")

    from django.test import Client
    bob_client = Client()
    bob_client.login(username='bob', password='pass123')
    response = bob_client.get('/applications/')

    assert response.status_code == 200
    assert b"AliceSecret" not in response.content


@pytest.mark.django_db
def test_user_cannot_edit_another_users_application():
    alice = User.objects.create_user('alice3', password='pass123')
    bob = User.objects.create_user('bob2', password='pass123')
    app = JobApplication.objects.create(user=alice, company="AliceCo", role="Engineer")

    from django.test import Client
    bob_client = Client()
    bob_client.login(username='bob2', password='pass123')
    response = bob_client.get(f'/applications/{app.pk}/edit/')

    assert response.status_code == 404  # get_object_or_404's user= filter blocks it