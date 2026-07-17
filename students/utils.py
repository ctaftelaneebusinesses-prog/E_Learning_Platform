from courses.models import Course, CourseSkill, LearningSession, StreakReward, StudentProgress, ActivityLog, StudentSkill
from django.utils.timezone import now
from students.openrouter_client import get_learning_suggestions

def check_and_award_streak_rewards(student, current_streak):
    rewards = StreakReward.objects.filter(
        is_active=True,
        streak_days__lte=current_streak
    )

    for reward in rewards:
        already_given = ActivityLog.objects.filter(
            student=student,
            activity_type='STREAK_REWARD',
            metadata__streak_days=reward.streak_days
        ).exists()

        if not already_given:
            # 🎁 Award XP
            progress_list = StudentProgress.objects.filter(student=student)

            for p in progress_list:
                p.xp_earned += reward.bonus_xp
                p.save()

            # 🧾 Log reward
            ActivityLog.objects.create(
                student=student,
                activity_type='STREAK_REWARD',
                metadata={
                    'streak_days': reward.streak_days,
                    'bonus_xp': reward.bonus_xp
                }
            )
            
def update_student_skills(student, course, earned_xp=0, base_points=0):
    """
    Update skill proficiency for a student based on course skill mapping.
    Safe, capped, and consistent.
    """

    course_skills = CourseSkill.objects.filter(course=course)

    for cs in course_skills:
        student_skill, _ = StudentSkill.objects.get_or_create(
            student=student,
            skill=cs.skill
        )

        # 🎯 Contribution calculation
        contribution = (earned_xp * 0.1 + base_points) * cs.weight

        # 🛑 Cap proficiency at 100
        student_skill.proficiency_score = min(
            student_skill.proficiency_score + contribution,
            100
        )

        student_skill.save()

def log_activity(student, activity_type, course=None, metadata=None):
    ActivityLog.objects.create(
        student=student,
        activity_type=activity_type,
        course=course,
        metadata=metadata or {}
    )
    
def start_learning_session(student, course):
    """
    Start a learning session if one is not already active.
    """
    active_session = LearningSession.objects.filter(
        student=student,
        course=course,
        end_time__isnull=True
    ).first()

    if not active_session:
        LearningSession.objects.create(
            student=student,
            course=course,
            start_time=now()
        )
        
def end_learning_session(student, course):
    """
    End the active learning session and calculate duration.
    """
    session = LearningSession.objects.filter(
        student=student,
        course=course,
        end_time__isnull=True
    ).first()

    if session:
        session.end_time = now()
        duration = session.end_time - session.start_time
        session.duration_minutes = max(
            int(duration.total_seconds() // 60),
            1
        )
        session.save()

from courses.models import CourseSkill, StudentSkill, LearningPath, Enrollment

def generate_ai_learning_path(student, role):
    """
    role example:
    - 'Computer Science Student'
    - 'Data Science Student'
    - 'Full Stack Developer'
    """

    try:
        technologies = get_learning_suggestions(role)

        # For now just return suggestions
        # Later we map → Course → Skill → Recommendation
        return technologies

    except Exception as e:
        print("OpenRouter Error:", e)
        return []
