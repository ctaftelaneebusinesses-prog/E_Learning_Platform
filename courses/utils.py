from courses.models import (
    Achievement,
    StudentAchievement,
    StudentProgress,
)

def check_and_award_achievements(student):
    achievements = Achievement.objects.filter(is_active=True)

    for achievement in achievements:
        # Skip if already earned
        if StudentAchievement.objects.filter(
            student=student,
            achievement=achievement
        ).exists():
            continue

        # 🔹 XP based achievement
        progress = StudentProgress.objects.filter(
            student=student
        ).first()

        if progress and progress.xp_earned >= achievement.xp_required:
            StudentAchievement.objects.create(
                student=student,
                achievement=achievement
            )
