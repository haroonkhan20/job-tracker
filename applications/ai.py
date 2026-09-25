"""
ai.py
-----
Compares a real job description against your ACTUAL saved resume content,
so "recommended resume" is a genuine judgment based on real skill overlap --
not a guess based on resume names.
"""

import json
from groq import Groq
from django.conf import settings


def extract_job_details(job_description_text, user_resumes):
    """
    user_resumes: a queryset/list of Resume objects belonging to the current user.
    """
    client = Groq(api_key=settings.GROQ_API_KEY)

    # Build a text block listing every real resume and its actual content,
    # so the model has genuine data to compare against -- not just names.
    resumes_block = "\n\n".join(
        f"--- RESUME: {r.name} ---\n{r.content}"
        for r in user_resumes
    )

    system_prompt = """You are helping a job seeker decide which of their existing
resumes best matches a job description. You will be given the full text of
several real resumes and one job description.

Compare the job description's required skills/technologies against what
ACTUALLY appears in each resume's content -- not the resume's name. Pick the
resume with the strongest genuine overlap.

Respond with ONLY valid JSON, no other text, in exactly this shape:
{
  "company": "string",
  "role": "string",
  "tech_stack": ["list", "of", "key", "technologies", "from", "the", "JD"],
  "recommended_resume": "the exact name of the best-matching resume from those provided",
  "matched_skills": ["skills", "that", "appear", "in", "both", "the", "JD", "and", "that", "resume"],
  "missing_skills": ["JD skills", "not", "found", "in", "any", "resume"],
  "match_percentage": "integer 0-100, your honest estimate of how well the BEST matching resume covers this JD's requirements",
  "reasoning": "one or two sentences explaining the match, citing specific overlapping skills"
}"""

    user_message = f"""JOB DESCRIPTION:
{job_description_text}

AVAILABLE RESUMES:
{resumes_block}"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def extract_resume_profile(resume_text):
    """
    Given raw pasted resume text, extract search-friendly keywords --
    NOT comparing against a JD this time, just characterizing the resume itself
    so we can build real job-board search URLs from it.
    """
    client = Groq(api_key=settings.GROQ_API_KEY)

    system_prompt = """You extract job-search keywords from a resume.
Respond with ONLY valid JSON, no other text, in exactly this shape:
{
  "job_titles": ["2-3 job titles this person should search for"],
  "top_skills": ["5-8 of their strongest, most searchable technical skills"],
  "search_query": "a short 3-6 word search string combining title + top skills, suitable for a job board search box"
}"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": resume_text},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)