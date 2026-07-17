from courses.models import StudentSkill
from career.models import JobRole


from .models import JobRole
from courses.models import StudentSkill


# --------------------------------------------------
# CORE: Job Readiness Calculator
# --------------------------------------------------
def calculate_job_readiness(student, job_role):
    """
    Calculates readiness % based on required skills
    """
    required_skills = job_role.required_skills.all()

    if not required_skills.exists():
        return 0

    # Student skill map
    student_skills = {
        ss.skill.id: ss.proficiency_score
        for ss in StudentSkill.objects.filter(student=student)
    }

    total = 0
    achieved = 0

    for skill in required_skills:
        total += 100
        achieved += min(student_skills.get(skill.id, 0), 100)

    return int((achieved / total) * 100)


# --------------------------------------------------
# MENTOR MESSAGE GENERATOR
# --------------------------------------------------
def mentor_message(job_title, readiness, required_skills, student_skills):
    missing = [
        skill.name
        for skill in required_skills
        if student_skills.get(skill.id, 0) < 60
    ]

    if readiness >= 90:
        return f"You are job-ready for {job_title}. You can apply now"

    if readiness >= 75:
        return (
            f"You are close to {job_title}. "
            f"Improve: {', '.join(missing[:3])}"
        )

    return (
        f"You are building skills for {job_title}. "
        f"Focus on: {', '.join(missing[:3])}"
    )


# --------------------------------------------------
# JOB SUGGESTIONS (MAIN ENTRY)
# --------------------------------------------------
def get_job_suggestions(student):
    """
    Returns sorted job suggestions with readiness % and mentor message
    """

    student_skills = {
        ss.skill.id: ss.proficiency_score
        for ss in StudentSkill.objects.filter(student=student)
    }

    suggestions = []

    for job in JobRole.objects.filter(is_active=True):
        readiness = calculate_job_readiness(student, job)

        if readiness >= job.min_readiness:
            suggestions.append({
                "job": job.title,                 # ✅ template compatible
                "readiness": readiness,           # ✅ progress bar
                "message": mentor_message(
                    job.title,
                    readiness,
                    job.required_skills.all(),
                    student_skills
                )
            })

    # Highest readiness first
    return sorted(suggestions, key=lambda x: x["readiness"], reverse=True)
