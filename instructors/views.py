from django.shortcuts import render, redirect, get_object_or_404
from .decorators import instructor_required
from courses.models import (
    Achievement,
    ActivityLog,
    Certificate,
    Course,
    CourseSkill,
    Enrollment,
    LearningSession,
    LearningStreak,
    Lesson,
    Question,
    Quiz,
    Skill,
    StreakReward,
    StudentProgress,
)
from django.db.models import Avg
from accounts.notifications import notify_students_of_instructor, notify_course_students


@instructor_required
def instructor_dashboard(request):
    instructor = request.user

    # Fetch instructor courses with enrollments prefetched
    courses = (
        Course.objects
        .filter(instructor=instructor)
        .prefetch_related("enrollment_set")
    )

    return render(
        request,
        "instructors/dashboard.html",
        {
            "courses": courses
        }
    )
def instructor_course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    enrollments = Enrollment.objects.filter(course=course).select_related("student")

    return render(request, "instructors/course_students.html", {
        "course": course,
        "enrollments": enrollments
    })
    
@instructor_required
def lesson_list(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
        instructor=request.user
    )
    lessons = course.lessons.all()
    return render(
        request,
        'instructors/lessons.html',
        {
            'course': course,
            'lessons': lessons
        }
    )


@instructor_required
def create_lesson(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
        instructor=request.user
    )

    if request.method == 'POST':
        Lesson.objects.create(
            course=course,
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            resource_link=request.POST.get('resource_link'),
            order=request.POST.get('order', 1),
            image=request.FILES.get('image')
        )
    return redirect('instructor_lesson_list', course_id=course.id)


@instructor_required
def toggle_lesson_status(request, lesson_id):
    lesson = get_object_or_404(
        Lesson,
        id=lesson_id,
        course__instructor=request.user
    )
    lesson.is_active = not lesson.is_active
    lesson.save()
    return redirect('instructor_lesson_list', course_id=lesson.course.id)

@instructor_required
def quiz_list(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
        instructor=request.user
    )
    quizzes = Quiz.objects.filter(course=course)

    return render(
        request,
        'instructors/quizzes.html',
        {
            'course': course,
            'quizzes': quizzes
        }
    )


@instructor_required
def create_quiz(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
        instructor=request.user
    )

    if request.method == 'POST':
        Quiz.objects.create(
            course=course,
            title=request.POST.get('title'),
            total_marks=request.POST.get('total_marks'),
            pass_mark=request.POST.get('pass_mark')
        )
    return redirect('instructor_quiz_list', course_id=course.id)


@instructor_required
def toggle_quiz_status(request, quiz_id):
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        course__instructor=request.user
    )
    quiz.is_active = not quiz.is_active
    quiz.save()
    return redirect('instructor_quiz_list', course_id=quiz.course.id)

@instructor_required
def question_list(request, quiz_id):
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        course__instructor=request.user
    )
    questions = quiz.questions.all()

    return render(
        request,
        'instructors/questions.html',
        {
            'quiz': quiz,
            'questions': questions
        }
    )


@instructor_required
def create_question(request, quiz_id):
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        course__instructor=request.user
    )

    if request.method == 'POST':
        Question.objects.create(
            quiz=quiz,
            text=request.POST.get('text'),
            option_a=request.POST.get('option_a'),
            option_b=request.POST.get('option_b'),
            option_c=request.POST.get('option_c'),
            option_d=request.POST.get('option_d'),
            correct_option=request.POST.get('correct_option'),
        )

    return redirect('instructor_question_list', quiz_id=quiz.id)


@instructor_required
def delete_question(request, question_id):
    question = get_object_or_404(
        Question,
        id=question_id,
        quiz__course__instructor=request.user
    )
    quiz_id = question.quiz.id
    question.delete()
    return redirect('instructor_question_list', quiz_id=quiz_id)

@instructor_required
def student_progress(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
        instructor=request.user
    )

    enrollments = Enrollment.objects.filter(course=course)

    progress_data = []
    for enrollment in enrollments:
        progress = StudentProgress.objects.filter(
            student=enrollment.student,
            course=course
        ).first()

        progress_data.append({
            'student': enrollment.student,
            'completed': progress.completed_lessons if progress else 0,
            'total': progress.total_lessons if progress else 0,
            'percentage': progress.completion_percentage if progress else 0,
            'xp': progress.xp_earned if progress else 0,
            'updated': progress.last_updated if progress else None,
        })

    return render(
        request,
        'instructors/student_progress.html',
        {
            'course': course,
            'progress_data': progress_data
        }
    )

@instructor_required
def instructor_analytics(request):
    courses = Course.objects.filter(instructor=request.user)

    analytics = []
    course_labels = []
    completion_values = []

    for course in courses:
        enroll_count = Enrollment.objects.filter(course=course).count()

        progress_qs = StudentProgress.objects.filter(course=course)

        avg_completion = progress_qs.aggregate(
            avg=Avg('completion_percentage')
        )['avg'] or 0

        avg_xp = progress_qs.aggregate(
            avg=Avg('xp_earned')
        )['avg'] or 0

        low_progress = progress_qs.filter(
            completion_percentage__lt=40
        ).count()

        quiz_count = Quiz.objects.filter(course=course).count()

        analytics.append({
            'course': course,
            'students': enroll_count,
            'avg_completion': round(avg_completion, 2),
            'avg_xp': round(avg_xp, 2),
            'low_progress': low_progress,
            'quiz_count': quiz_count,
        })
        course_labels.append(course.title)
        completion_values.append(round(avg_completion, 2))


    return render(
        request,
        'instructors/analytics.html',
        {
            'analytics': analytics,
            'course_labels': course_labels,
            'completion_values': completion_values,
        }
    )


@instructor_required
def progress_overview(request):
    progress_records = StudentProgress.objects.select_related(
        'student', 'course'
    ).filter(course__instructor=request.user)

    return render(
        request,
        'instructors/progress.html',
        {'progress_records': progress_records}
    )


@instructor_required
def achievement_list(request):
    achievements = Achievement.objects.all()
    return render(
        request,
        'instructors/achievements.html',
        {'achievements': achievements}
    )


@instructor_required
def create_achievement(request):
    if request.method == 'POST':
        achievement = Achievement.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            xp_required=request.POST.get('xp_required')
        )
        notify_students_of_instructor(
            request.user,
            f"New achievement added: {achievement.title}"
        )
    return redirect('instructor_achievement_list')


@instructor_required
def toggle_achievement_status(request, achievement_id):
    achievement = get_object_or_404(Achievement, id=achievement_id)
    achievement.is_active = not achievement.is_active
    achievement.save()
    return redirect('instructor_achievement_list')


@instructor_required
def streak_overview(request):
    streaks = LearningStreak.objects.select_related('student').filter(
        student__profile__role='STUDENT',
        student__enrollment__course__instructor=request.user
    ).distinct()
    rewards = StreakReward.objects.all()

    return render(
        request,
        'instructors/streaks.html',
        {
            'streaks': streaks,
            'rewards': rewards
        }
    )


@instructor_required
def create_streak_reward(request):
    if request.method == 'POST':
        reward = StreakReward.objects.create(
            streak_days=request.POST.get('streak_days'),
            bonus_xp=request.POST.get('bonus_xp')
        )
        notify_students_of_instructor(
            request.user,
            f"New streak reward added: {reward.streak_days}-day streak → {reward.bonus_xp} XP"
        )
    return redirect('instructor_streaks')


@instructor_required
def skill_list(request):
    skills = Skill.objects.all()
    courses = Course.objects.filter(instructor=request.user)
    mappings = CourseSkill.objects.select_related('course', 'skill').filter(
        course__instructor=request.user
    )

    return render(
        request,
        'instructors/skills.html',
        {
            'skills': skills,
            'courses': courses,
            'mappings': mappings
        }
    )


@instructor_required
def create_skill(request):
    if request.method == 'POST':
        skill = Skill.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        notify_students_of_instructor(request.user, f"New skill added: {skill.name}")
    return redirect('instructor_skill_list')


@instructor_required
def map_course_skill(request):
    if request.method == 'POST':
        course = get_object_or_404(
            Course,
            id=request.POST.get('course'),
            instructor=request.user
        )
        mapping = CourseSkill.objects.create(
            course=course,
            skill_id=request.POST.get('skill'),
            weight=request.POST.get('weight', 1)
        )
        notify_course_students(
            course,
            f"New skill added to {course.title}: {mapping.skill.name}"
        )
    return redirect('instructor_skill_list')


@instructor_required
def time_tracking_overview(request):
    sessions = LearningSession.objects.select_related(
        'student', 'course'
    ).filter(course__instructor=request.user).order_by('-start_time')[:100]

    activities = ActivityLog.objects.select_related(
        'student', 'course'
    ).filter(course__instructor=request.user).order_by('-timestamp')[:100]

    return render(
        request,
        'instructors/time_tracking.html',
        {
            'sessions': sessions,
            'activities': activities
        }
    )


@instructor_required
def certificate_list(request):
    certificates = (
        Certificate.objects
        .select_related('student', 'course')
        .filter(course__instructor=request.user)
        .order_by('-issued_at')
    )

    courses = Course.objects.filter(instructor=request.user)

    course_id = request.GET.get('course')
    if course_id:
        certificates = certificates.filter(course_id=course_id)

    return render(
        request,
        'instructors/certificates.html',
        {
            'certificates': certificates,
            'courses': courses,
            'selected_course': course_id
        }
    )


@instructor_required
def revoke_certificate(request, certificate_id):
    certificate = get_object_or_404(
        Certificate, id=certificate_id, course__instructor=request.user
    )
    certificate.is_active = False
    certificate.save()
    return redirect('instructor_certificate_list')


@instructor_required
def reissue_certificate(request, certificate_id):
    certificate = get_object_or_404(
        Certificate, id=certificate_id, course__instructor=request.user
    )
    certificate.is_active = True
    certificate.save()
    return redirect('instructor_certificate_list')
