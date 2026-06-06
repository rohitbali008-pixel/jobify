import re

from .models import Application


def normalize_skills(skill_string):
    """
    Convert:
    'Python, Django, REST API'
    ->
    {'python', 'django', 'rest api'}
    """

    if not skill_string:
        return set()

    return {
        skill.strip().lower()
        for skill in skill_string.split(",")
        if skill.strip()
    }


def skill_score(candidate_skills, required_skills):
    """
    Returns score between 0-100
    """

    candidate = normalize_skills(candidate_skills)
    required = normalize_skills(required_skills)

    if not required:
        return 0

    matched = candidate.intersection(required)

    return round(
        (len(matched) / len(required)) * 100,
        2
    )


def experience_score(candidate_exp, required_exp):
    """
    Returns score between 0-100
    """

    candidate_exp = candidate_exp or 0
    required_exp = required_exp or 0

    if required_exp <= 0:
        return 100

    if candidate_exp >= required_exp:
        return 100

    return round(
        (candidate_exp / required_exp) * 100,
        2
    )


def education_score(candidate_edu, required_edu):
    """
    Returns score between 0-100
    """

    if not candidate_edu or not required_edu:
        return 0

    candidate_edu = candidate_edu.lower().strip()
    required_edu = required_edu.lower().strip()

    # Exact match
    if candidate_edu == required_edu:
        return 100

    candidate_words = set(re.findall(r"\w+", candidate_edu))
    required_words = set(re.findall(r"\w+", required_edu))

    if not required_words:
        return 0

    common_words = candidate_words.intersection(required_words)

    return round(
        (len(common_words) / len(required_words)) * 100,
        2
    )


def calculate_ats_score(application):
    """
    Calculate ATS score for one application
    """

    job = application.job_id

    profile = getattr(application.user_id, "profile", None)

    skill = skill_score(
        application.skills,
        job.skills
    )

    exp = experience_score(
        application.experience,
        job.experience
    )

    edu = 0

    if profile:
        edu = education_score(
            profile.education,
            job.qualification
        )

    final_score = (
        (skill * 0.60) +
        (exp * 0.25) +
        (edu * 0.15)
    )

    return round(final_score, 2)


def generate_job_scores(job):
    """
    Generate ATS score for all applications of a job
    """

    applications = Application.objects.filter(
        job_id=job
    ).select_related(
        "user_id",
        "job_id"
    )

    for application in applications:

        ats_score = calculate_ats_score(application)

        application.ats_score = ats_score

        # Optional auto status update
        if ats_score >= 80:
            application.status = "Shortlisted"

        elif ats_score < 40:
            application.status = "Rejected"

        else:
            application.status = "Under Review"

        application.save(
            update_fields=[
                "ats_score",
                "status"
            ]
        )

    return True