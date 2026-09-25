from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.contrib import messages
import json

from .models import JobApplication, Resume
from .forms import JobApplicationForm, ResumeForm
from .ai import extract_job_details

from urllib.parse import quote_plus
from .ai import extract_resume_profile


@login_required
def resume_job_search(request):
    if request.method == 'POST':
        resume_text = request.POST.get('resume_text', '')
        try:
            profile = extract_resume_profile(resume_text)
            query = profile.get('search_query', '')
            encoded = quote_plus(query)

            links = {
                'LinkedIn': f"https://www.linkedin.com/jobs/search/?keywords={encoded}",
                'Indeed': f"https://www.indeed.com/jobs?q={encoded}",
                'Internshala': f"https://internshala.com/internships/keywords-{encoded}",
                'Wellfound': f"https://wellfound.com/jobs?query={encoded}",
            }

            return render(request, 'applications/resume_search_results.html', {
                'profile': profile,
                'links': links,
            })
        except Exception as e:
            messages.error(request, f"AI search failed: {e}")
            return redirect('home')

    return render(request, 'applications/resume_search_form.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'applications/signup.html', {'form': form})


@login_required
def home(request):
    return render(request, 'applications/home.html')


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('login')
    return render(request, 'applications/confirm_delete_account.html')


@login_required
def application_list(request):
    applications = JobApplication.objects.filter(user=request.user)
    return render(request, 'applications/list.html', {'applications': applications})


@login_required
def application_create(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, f"Added application to {application.company}")
            return redirect('application_list')
    else:
        form = JobApplicationForm()
    return render(request, 'applications/form.html', {
        'form': form, 'title': 'Add Application', 'form_action': 'application_create',
    })


@login_required
def application_edit(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated {application.company}")
            return redirect('application_list')
    else:
        form = JobApplicationForm(instance=application)
    return render(request, 'applications/form.html', {
        'form': form, 'title': 'Edit Application',
        'form_action': 'application_edit', 'form_pk': application.pk,
    })


@login_required
def application_delete(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == 'POST':
        application.delete()
        messages.success(request, "Application deleted")
        return redirect('application_list')
    return render(request, 'applications/confirm_delete.html', {'application': application})


@login_required
def ai_prefill(request):
    if request.method == 'POST':
        job_description = request.POST.get('job_description', '')
        user_resumes = Resume.objects.filter(user=request.user)

        if not user_resumes.exists():
            messages.error(request, "You haven't added any resumes yet — add one under 'My Resumes' first.")
            return redirect('application_create')

        try:
            extracted = extract_job_details(job_description, user_resumes)
            match_pct = int(extracted.get('match_percentage', 0))
            match_pct = max(0, min(100, match_pct))  # clamp to a safe 0-100 range

            if match_pct < 40:
                match_color = '#dc2626'  # red
            elif match_pct < 60:
                match_color = '#f97316'  # orange
            elif match_pct < 75:
                match_color = '#eab308'  # yellow
            else:
                match_color = '#16a34a'  # green

            needle_rotation = (match_pct * 1.8) - 90  # maps 0-100 to -90deg..+90deg

            form = JobApplicationForm(initial={
                'company': extracted.get('company', ''),
                'role': extracted.get('role', ''),
                'resume_version': extracted.get('recommended_resume', ''),
                'notes': f"Tech stack: {', '.join(extracted.get('tech_stack', []))}\n"
                         f"Matched skills: {', '.join(extracted.get('matched_skills', []))}\n"
                         f"Missing skills: {', '.join(extracted.get('missing_skills', []))}\n"
                         f"Match: {match_pct}%\n"
                         f"Reasoning: {extracted.get('reasoning', '')}",
            })
            return render(request, 'applications/form.html', {
                'form': form,
                'title': 'Add Application (AI-prefilled — review before saving)',
                'form_action': 'application_create',
                'match_pct': match_pct,
                'match_color': match_color,
                'needle_rotation': needle_rotation,
            })
        except Exception as e:
            messages.error(request, f"AI extraction failed: {e}. You can still add it manually.")
            return redirect('application_create')

    return render(request, 'applications/ai_prefill.html')


@login_required
def resume_list(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'applications/resume_list.html', {'resumes': resumes})


@login_required
def resume_create(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            messages.success(request, f"Added resume: {resume.name}")
            return redirect('resume_list')
    else:
        form = ResumeForm()
    return render(request, 'applications/resume_form.html', {'form': form})


@login_required
def resume_delete(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        resume.delete()
        messages.success(request, "Resume deleted")
        return redirect('resume_list')
    return render(request, 'applications/confirm_delete.html', {'application': resume})