from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views

from . import views
from .api import JobApplicationViewSet

router = DefaultRouter()
router.register(r'applications', JobApplicationViewSet, basename='api-application')

urlpatterns = [
    path('', views.home, name='home'),
    path('applications/', views.application_list, name='application_list'),
    path('applications/new/', views.application_create, name='application_create'),
    path('applications/<int:pk>/edit/', views.application_edit, name='application_edit'),
    path('applications/<int:pk>/delete/', views.application_delete, name='application_delete'),

    path('resumes/', views.resume_list, name='resume_list'),
    path('resumes/new/', views.resume_create, name='resume_create'),
    path('resumes/<int:pk>/delete/', views.resume_delete, name='resume_delete'),

    path('ai-prefill/', views.ai_prefill, name='ai_prefill'),

    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='applications/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('delete-account/', views.delete_account, name='delete_account'),

    path('api/', include(router.urls)),
    path('resume-job-search/', views.resume_job_search, name='resume_job_search'),
]