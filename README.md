# JobTracker — AI-Powered Job Application Tracker

A full-stack Django web application for managing a job search — not just a CRUD demo. Paste a job description, get it compared against your actual saved resumes by a real LLM (match percentage, matched/missing skills, resume recommendation), and let a background job pipeline automatically flag applications that need a follow-up.

Built as a personal tool while job-hunting, and as a demonstration of production-pattern backend architecture: multi-service Docker deployment, real auth/multi-user data isolation, background task processing, and honest AI integration (not a chatbot bolted on for show).

## Features

- **Full auth system** — signup, login, logout, account deletion, with strict per-user data isolation (verified by automated tests, not just assumed)
- **Full CRUD** on job applications — company, role, status, resume version used, notes, dates
- **AI-powered JD matching** — paste a job description, get it compared against your real saved resume content (not just resume names) using Groq's LLM with structured JSON output, including an honest 0–100% match score visualized as a colored gauge
- **AI-powered job search** — paste a resume, get real, correctly-formatted search links to LinkedIn, Indeed, Internshala, and Wellfound with AI-extracted keywords
- **Background job pipeline** — Celery + Redis + Celery Beat automatically scans daily for applications sitting 14+ days with no response, flagging them for follow-up
- **REST API layer** (Django REST Framework) alongside the server-rendered pages — same data, two interfaces
- **PostgreSQL** — a real client-server database, not SQLite
- **8 automated tests** (pytest) covering business logic and, critically, that one user can never see another user's data
- **Dockerized** — 4 coordinated services (Django, PostgreSQL, Redis, Celery worker) via Docker Compose

## Tech Stack

Python · Django · Django REST Framework · PostgreSQL · Celery · Redis · Groq LLM API · Docker · pytest

## Architecture


┌─────────────┐ ┌──────────────┐ ┌────────────┐
│ Django │────▶│ PostgreSQL │ │ Groq API │
│ (web app) │ └──────────────┘ │ (LLM) │
└──────┬──────┘ └─────▲──────┘
│ │
│ triggers used by AI features
▼ │
┌─────────────┐ ┌──────────────┐ │
│Celery Worker│◀────│ Redis │────────────┘
│ │ │ (broker) │
└──────▲──────┘ └──────▲───────┘
│ │
│ ┌──────┴──────┐
└────────────│ Celery Beat │
│ (scheduler) │
└─────────────┘



## Setup — Local (without Docker)

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Set up PostgreSQL and Redis locally, then create a .env file:
DB_NAME=job_tracker
DB_USER=appuser
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
GROQ_API_KEY=your_groq_key

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

In separate terminals, for the background job pipeline:
```bash
celery -A jobtracker worker --loglevel=info --pool=solo   # Windows needs --pool=solo
celery -A jobtracker beat --loglevel=info
```

## Setup — Docker

```bash
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Running tests

```bash
pytest applications/ -v
```

8 tests: model business logic (follow-up detection, day calculations) and view-level security (auth enforcement, and — the most important one — verifying one user genuinely cannot see or edit another user's data).

## The AI features, honestly described

**JD matching** feeds the *actual text content* of a user's saved resumes into the LLM alongside the pasted job description, asking it to compare real skill overlap and return a structured, honest match percentage — not a resume-name lookup. The AI's output pre-fills a form the user still reviews and saves themselves; nothing is written to the database automatically.

**Job search** does *not* scrape LinkedIn/Indeed/Internshala — that would violate their Terms of Service. Instead, it extracts search-relevant keywords from a resume and generates correctly-formatted, direct search URLs to each platform.

## Honest limitations

- Docker's `worker` service is defined but Celery Beat isn't yet containerized (currently run manually alongside Docker Compose) — a natural next step
- No CI pipeline yet
- Not deployed publicly yet — runs locally / via Docker Compose

## What I'd add next

- GitHub Actions CI running the test suite against real Postgres/Redis service containers
- Celery Beat as its own Docker service
- Public hosting (Render/Railway)