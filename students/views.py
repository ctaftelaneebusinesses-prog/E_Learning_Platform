# # from django.conf import settings
# # import os
# # from reportlab.lib.utils import ImageReader
# from django.http import HttpResponse
# from django.shortcuts import render, redirect, get_object_or_404
# from django.utils.timezone import now
# from django.db.models import Sum
# from accounts.decorators import student_required
# from courses.models import ActivityLog, Course, LearningPath, Lesson, LessonCompletion, StreakReward, StudentAchievement, StudentSkill
# from courses.models import Enrollment, StudentProgress
# from datetime import timedelta
# from django.utils.timezone import localdate
# from courses.models import LearningStreak
# from courses.utils import check_and_award_achievements
# from courses.models import Quiz, StudentQuizAttempt
# from students.utils import check_and_award_streak_rewards, generate_ai_learning_path
# from students.utils import start_learning_session, end_learning_session
# from students.utils import update_student_skills
# from students.utils import log_activity
# import uuid
# from courses.models import Certificate
# from django.template.loader import get_template
# from xhtml2pdf import pisa
# import io
# from reportlab.lib.pagesizes import A4, landscape
# from reportlab.pdfgen import canvas
# from reportlab.lib.colors import HexColor
# from reportlab.lib.units import inch
# from career.services import get_job_suggestions

# # -------------------------
# # STUDENT DASHBOARD
# # -------------------------
# @student_required
# def student_dashboard(request):
#     enrollments = Enrollment.objects.filter(student=request.user)

#     progress_map = {
#         p.course_id: p
#         for p in StudentProgress.objects.filter(student=request.user)
#     }

#     streak = LearningStreak.objects.filter(
#         student=request.user
#     ).first()

#     total_xp = sum(
#         p.xp_earned
#         for p in StudentProgress.objects.filter(student=request.user)
#     )
#     job_suggestions = get_job_suggestions(request.user)
    
#     return render(
#         request,
#         'students/dashboard.html',
#         {
#             'enrollments': enrollments,
#             'progress_map': progress_map,
#             'streak': streak,
#             'total_xp' : total_xp,
#             'job_suggestions': job_suggestions
            
#         }
#     )


# # -------------------------
# # COURSE CATALOG (NOT ENROLLED)
# # -------------------------
# @student_required
# def course_catalog(request):
#     enrolled_course_ids = Enrollment.objects.filter(
#         student=request.user
#     ).values_list('course_id', flat=True)

#     courses = Course.objects.filter(
#         is_active=True
#     ).exclude(id__in=enrolled_course_ids)

#     return render(
#         request,
#         'students/courses.html',
#         {
#             'courses': courses
#         }
#     )


# # -------------------------
# # ENROLL COURSE
# # -------------------------
# @student_required
# def enroll_course(request, course_id):
#     course = get_object_or_404(
#         Course,
#         id=course_id,
#         is_active=True
#     )

#     enrollment, created = Enrollment.objects.get_or_create(
#         student=request.user,
#         course=course
#     )

#     if created:
#         total_lessons = course.lessons.filter(is_active=True).count()

#         StudentProgress.objects.create(
#             student=request.user,
#             course=course,
#             completed_lessons=0,
#             total_lessons=total_lessons,
#             completion_percentage=0,
#             xp_earned=0
#         )

#         # 🔔 ACTIVITY LOG (NEW)
#         log_activity(
#             student=request.user,
#             activity_type='COURSE_ENROLL',
#             course=course
#         )

#     return redirect('student_dashboard')

# # -------------------------
# # MY COURSES
# # -------------------------
# @student_required
# def my_courses(request):
#     enrollments = Enrollment.objects.filter(student=request.user)

#     certified_course_ids = set(
#         Certificate.objects.filter(
#             student=request.user,
#             is_active=True
#         ).values_list('course_id', flat=True)
#     )

#     return render(
#         request,
#         'students/my_courses.html',
#         {
#             'enrollments': enrollments,
#             'certified_course_ids': certified_course_ids
#         }
#     )
    
# # -------------------------
# # LESSON LIST
# # -------------------------
# @student_required
# def lesson_list(request, course_id):
#     course = get_object_or_404(Course, id=course_id)

#     # Ensure enrollment
#     if not Enrollment.objects.filter(
#         student=request.user,
#         course=course
#     ).exists():
#         return redirect('student_dashboard')
    
#     # ⏱️ START learning session
#     start_learning_session(
#         student=request.user,
#         course=course
#     )


#     lessons = Lesson.objects.filter(
#         course=course,
#         is_active=True
#     ).order_by('order')

#     progress = StudentProgress.objects.filter(
#         student=request.user,
#         course=course
#     ).first()

#     completed = progress.completed_lessons if progress else 0
#     total = lessons.count()

#     return render(
#         request,
#         'students/lessons.html',
#         {
#             'course': course,
#             'lessons': lessons,
#             'completed': completed,
#             'total': total
#         }
#     )


# # -------------------------
# # LESSON DETAIL
# # -------------------------
# @student_required
# def lesson_detail(request, lesson_id):
#     lesson = get_object_or_404(
#         Lesson,
#         id=lesson_id,
#         is_active=True
#     )

#     # Ensure enrollment
#     get_object_or_404(
#         Enrollment,
#         student=request.user,
#         course=lesson.course
#     )

#     progress, _ = StudentProgress.objects.get_or_create(
#         student=request.user,
#         course=lesson.course
#     )

#     already_completed = LessonCompletion.objects.filter(
#         student=request.user,
#         lesson=lesson
#     ).exists()

#     if request.method == 'POST' and not already_completed:
#         # ✅ Mark lesson completed
#         LessonCompletion.objects.create(
#             student=request.user,
#             lesson=lesson
#         )

#         # ✅ SAFE progress recalculation (SOURCE OF TRUTH)
#         completed_count = LessonCompletion.objects.filter(
#             student=request.user,
#             lesson__course=lesson.course
#         ).count()

#         total_lessons = Lesson.objects.filter(
#             course=lesson.course,
#             is_active=True
#         ).count()

#         progress.completed_lessons = completed_count
#         progress.total_lessons = total_lessons

#         if total_lessons > 0:
#             progress.completion_percentage = min(
#                 round((completed_count / total_lessons) * 100, 2),
#                 100
#             )
#         else:
#             progress.completion_percentage = 0

#         # 🎮 XP for lesson (safe)
#         progress.xp_earned += 10
#         progress.last_updated = now()
#         progress.save()
        
#         # 🎓 CERTIFICATE ISSUE LOGIC (ON COURSE COMPLETION)
#         if progress.completion_percentage == 100:
#             Certificate.objects.get_or_create(
#                 student=request.user,
#                 course=lesson.course,
#                 defaults={
#                     'certificate_id': f"CERT-{uuid.uuid4().hex[:12].upper()}"
#                 }
#             )

        
#         log_activity(
#             student=request.user,
#             activity_type='LESSON_VIEW',
#             course=lesson.course,
#             metadata={
#                 'lesson_title': lesson.title
#             }
#         )


#         # 🏆 Achievement check
#         check_and_award_achievements(request.user)
        
        

        
#         update_student_skills(
#             student=request.user,
#             course=lesson.course,
#             base_points=5
#         )

#         # 🔥 LEARNING STREAK LOGIC
#         today = localdate()
#         streak, _ = LearningStreak.objects.get_or_create(student=request.user)

#         if streak.last_activity_date == today:
#             pass
#         elif streak.last_activity_date == today - timedelta(days=1):
#             streak.current_streak += 1
#         else:
#             streak.current_streak = 1

#         streak.last_activity_date = today
#         streak.longest_streak = max(
#             streak.longest_streak,
#             streak.current_streak
#         )
#         streak.save()
        
#         check_and_award_streak_rewards(
#             request.user,
#             streak.current_streak
#         )
        
#         # ⏱️ END learning session
#         end_learning_session(
#             student=request.user,
#             course=lesson.course
#         )



#         return redirect(
#             'student_lesson_list',
#             course_id=lesson.course.id
#         )

#     # ✅ GET request response
#     return render(
#         request,
#         'students/lesson_detail.html',
#         {
#             'lesson': lesson,
#             'progress': progress,
#             'already_completed': already_completed
#         }
#     )
    
# @student_required
# def view_certificate(request, course_id):
#     course = get_object_or_404(
#         Course,
#         id=course_id
#     )

#     certificate = get_object_or_404(
#         Certificate,
#         student=request.user,
#         course=course,
#         is_active=True
#     )

#     return render(
#         request,
#         'students/certificate.html',
#         {
#             'certificate': certificate,
#             'course': course,
#             'student': request.user
#         }
#     )

# @student_required
# def download_certificate_pdf(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     certificate = get_object_or_404(
#         Certificate,
#         student=request.user,
#         course=course,
#         is_active=True
#     )

#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = (
#         f'inline; filename=certificate_{course.id}.pdf'
#     )

#     # A4 Landscape
#     width, height = landscape(A4)
#     c = canvas.Canvas(response, pagesize=(width, height))

#     # COLORS
#     blue = HexColor("#1f4fd8")
#     green = HexColor("#2e7d32")
# # IMAGE PATHS
#     # logo_path = os.path.join(settings.BASE_DIR, "static/images/logo.png")
#     # seal_path = os.path.join(settings.BASE_DIR, "static/images/seal.png")

#     # BORDER
#     c.setStrokeColor(blue)
#     c.setLineWidth(4)
#     c.rect(30, 30, width - 60, height - 60)
# #     # LOGO (top left)
# #     c.drawImage(
# #     ImageReader(logo_path),
# #     60,
# #     height - 120,
# #     width=120,
# #     height=60,
# #     mask='auto'
# # )

# # # SEAL (top right)
# #     c.drawImage(
# #     ImageReader(seal_path),
# #     width - 160,
# #     height - 130,
# #     width=80,
# #     height=80,
# #     mask='auto'
# # )

# #     # TITLE
#     c.setFont("Helvetica-Bold", 28)
#     c.setFillColor(blue)
#     c.drawCentredString(width / 2, height - 100, "Certificate of Completion")

#     # SUBTITLE
#     c.setFont("Helvetica", 16)
#     c.setFillColor(HexColor("#000000"))
#     c.drawCentredString(width / 2, height - 160, "This is to certify that")

#     # STUDENT NAME
#     c.setFont("Helvetica-Bold", 22)
#     c.drawCentredString(
#         width / 2,
#         height - 210,
#         request.user.get_full_name() or request.user.username
#     )

#     # TEXT
#     c.setFont("Helvetica", 16)
#     c.drawCentredString(
#         width / 2,
#         height - 260,
#         "has successfully completed the course"
#     )

#     # COURSE NAME
#     c.setFont("Helvetica-Bold", 20)
#     c.setFillColor(green)
#     c.drawCentredString(
#         width / 2,
#         height - 310,
#         course.title
#     )

#     # DESCRIPTION
#     c.setFont("Helvetica", 14)
#     c.setFillColor(HexColor("#000000"))
#     c.drawCentredString(
#         width / 2,
#         height - 360,
#         "The student has demonstrated the required knowledge and skills"
#     )

#     # FOOTER INFO
#     c.setFont("Helvetica", 12)

#     # Left
#     c.drawString(
#         80,
#         120,
#         f"Certificate ID: {certificate.certificate_id}"
#     )
#     c.drawString(
#         80,
#         95,
#         f"Instructor: {course.instructor.get_full_name() if course.instructor else '—'}"
#     )

#     # Right
#     c.drawRightString(
#         width - 80,
#         120,
#         f"Issued On: {certificate.issued_at.strftime('%d %b %Y')}"
#     )
#     c.drawRightString(
#         width - 80,
#         95,
#         "Platform: E-Learning Platform"
#     )

#     c.showPage()
#     c.save()

#     return response

# @student_required
# def student_achievements(request):
#     achievements = StudentAchievement.objects.filter(
#         student=request.user
#     ).select_related('achievement')

#     return render(
#         request,
#         'students/achievements.html',
#         {
#             'achievements': achievements
#         }
#     )

# @student_required
# def student_leaderboard(request):
#     leaderboard = (
#         StudentProgress.objects
#         .values('student__username', 'student_id')
#         .annotate(total_xp=Sum('xp_earned'))
#         .order_by('-total_xp')
#     )

#     streak_map = {
#         s.student_id: s
#         for s in LearningStreak.objects.all()
#     }

#     ranked = []
#     rank = 1

#     for entry in leaderboard:
#         streak = streak_map.get(entry['student_id'])
#         ranked.append({
#             'rank': rank,
#             'username': entry['student__username'],
#             'xp': entry['total_xp'],
#             'current_streak': streak.current_streak if streak else 0,
#             'longest_streak': streak.longest_streak if streak else 0
#         })
#         rank += 1

#     return render(
#         request,
#         'students/leaderboard.html',
#         {
#             'leaderboard': ranked
#         }
#     )

# @student_required
# def student_quiz_list(request, course_id):
#     course = get_object_or_404(Course, id=course_id)

#     get_object_or_404(
#         Enrollment,
#         student=request.user,
#         course=course
#     )

#     quizzes = Quiz.objects.filter(
#         course=course,
#         is_active=True
#     )

#     attempts = {
#         a.quiz_id: a
#         for a in StudentQuizAttempt.objects.filter(
#             student=request.user,
#             quiz__course=course
#         )
#     }


#     return render(
#         request,
#         'students/quizzes.html',
#         {
#             'course': course,
#             'quizzes': quizzes,
#             'attempts': attempts
#         }
#     )

# @student_required
# def attempt_quiz(request, quiz_id):
#     quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)

#     get_object_or_404(
#         Enrollment,
#         student=request.user,
#         course=quiz.course
#     )
    
#     # ⏱️ START learning session (quiz)
#     start_learning_session(
#         student=request.user,
#         course=quiz.course
#     )


#     attempt = StudentQuizAttempt.objects.filter(
#         student=request.user,
#         quiz=quiz
#     ).first()

#     # ❌ Block if already passed
#     if attempt and attempt.passed:
#         return redirect('student_quiz_list', course_id=quiz.course.id)

#     questions = quiz.questions.all()

#     if request.method == 'POST':
#         score = 0
#         per_question = quiz.total_marks // questions.count()

#         for q in questions:
#             selected = request.POST.get(str(q.id))
#             if selected == q.correct_option:
#                 score += per_question

#         passed = score >= quiz.pass_mark

#         StudentQuizAttempt.objects.update_or_create(
#             student=request.user,
#             quiz=quiz,
#             defaults={
#                 'score': score,
#                 'passed': passed
#             }
#         )
        
#         # 🔔 ACTIVITY LOG — QUIZ ATTEMPT
#         log_activity(
#             student=request.user,
#             activity_type='QUIZ_ATTEMPT',
#             course=quiz.course,
#             metadata={
#                 'quiz': quiz.title,
#                 'score': score,
#                 'passed': passed
#             }
#         )

#         if passed:
#             progress = StudentProgress.objects.get(
#                 student=request.user,
#                 course=quiz.course
#             )

#             quiz_xp = quiz.pass_mark // 2
#             progress.xp_earned += quiz_xp
#             progress.last_updated = now()
#             progress.save()
            
#             update_student_skills(
#                 student=request.user,
#                 course=quiz.course,
#                 earned_xp=quiz_xp
#             )

#             check_and_award_achievements(request.user)
            
            


        
#         # ⏱️ END learning session
#         end_learning_session(
#             student=request.user,
#             course=quiz.course
#         )
        
#         return redirect(
#             'student_quiz_list',
#             course_id=quiz.course.id
#         )


#     return render(
#         request,
#         'students/attempt_quiz.html',
#         {
#             'quiz': quiz,
#             'questions': questions
#         }
#     )

# @student_required
# def streak_rewards(request):
#     streak = LearningStreak.objects.filter(
#         student=request.user
#     ).first()

#     rewards = StreakReward.objects.filter(is_active=True).order_by('streak_days')

#     earned = ActivityLog.objects.filter(
#         student=request.user,
#         activity_type='STREAK_REWARD'
#     )

#     earned_days = {
#         log.metadata.get('streak_days')
#         for log in earned if log.metadata
#     }

#     return render(
#         request,
#         'students/streak_rewards.html',
#         {
#             'streak': streak,
#             'rewards': rewards,
#             'earned_days': earned_days
#         }
#     )

# @student_required
# def student_skills(request):
#     skills = StudentSkill.objects.filter(student=request.user)

#     return render(
#         request,
#         'students/skills.html',
#         {
#             'skills': skills
#         }
#     )

# @student_required
# def activity_timeline(request):
#     activities = ActivityLog.objects.filter(
#         student=request.user
#     ).order_by('-timestamp')[:100]

#     return render(
#         request,
#         'students/activity_timeline.html',
#         {
#             'activities': activities
#         }
#     )

# @student_required
# def ai_learning_path(request):
#     suggestions = []
#     role = None

#     if request.method == "POST":
#         role = request.POST.get("role")

#         if role:
#             suggestions = generate_ai_learning_path(
#                 student=request.user,
#                 role=role
#             )

#     return render(
#         request,
#         'students/ai_learning_path.html',
#         {
#             'role': role,
#             'suggestions': suggestions
#         }
#     )

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from django.db.models import Sum
from django.templatetags.static import static
from accounts.decorators import student_required
from courses.models import ActivityLog, Course, LearningPath, Lesson, LessonCompletion, StreakReward, StudentAchievement, StudentSkill
from courses.models import Enrollment, StudentProgress, AILearningPathQuery
from datetime import timedelta
from django.utils.timezone import localdate
from courses.models import LearningStreak
from courses.utils import check_and_award_achievements
from courses.models import Quiz, StudentQuizAttempt
from students.utils import check_and_award_streak_rewards, generate_ai_learning_path
from students.utils import start_learning_session, end_learning_session
from students.utils import update_student_skills
from students.utils import log_activity
import uuid
from courses.models import Certificate
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from career.services import get_job_suggestions
from courses.models import Achievement


# -------------------------
# STUDENT DASHBOARD
# -------------------------
@student_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user)

    progress_map = {
        p.course_id: p
        for p in StudentProgress.objects.filter(student=request.user)
    }

    streak = LearningStreak.objects.filter(
        student=request.user
    ).first()

    total_xp = sum(
        p.xp_earned
        for p in StudentProgress.objects.filter(student=request.user)
    )

    profile = getattr(request.user, 'profile', None)
    is_school_student = bool(profile and profile.education_type == 'SCHOOL')

    job_suggestions = None
    achievements = None

    if is_school_student:
        check_and_award_achievements(request.user)
        earned_ids = set(
            StudentAchievement.objects.filter(student=request.user)
            .values_list('achievement_id', flat=True)
        )
        achievements = [
            {
                'title': a.title,
                'message': a.description,
                'icon': 'bi-trophy-fill' if a.id in earned_ids else 'bi-lock-fill',
                'unlocked': a.id in earned_ids,
            }
            for a in Achievement.objects.filter(is_active=True).order_by('xp_required')
        ]
    else:
        job_suggestions = get_job_suggestions(request.user)

    return render(
        request,
        'students/dashboard.html',
        {
            'enrollments': enrollments,
            'progress_map': progress_map,
            'streak': streak,
            'total_xp': total_xp,
            'job_suggestions': job_suggestions,
            'achievements': achievements,
        }
    )


# -------------------------
# COURSE CATALOG (NOT ENROLLED)
# -------------------------
@student_required
def course_catalog(request):
    enrolled_course_ids = Enrollment.objects.filter(
        student=request.user
    ).values_list('course_id', flat=True)

    courses = Course.objects.filter(
        is_active=True
    ).exclude(id__in=enrolled_course_ids)

    return render(
        request,
        'students/courses.html',
        {
            'courses': courses
        }
    )


# -------------------------
# ENROLL COURSE
# -------------------------
@student_required
def enroll_course(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
        is_active=True
    )

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )

    if created:
        total_lessons = course.lessons.filter(is_active=True).count()

        StudentProgress.objects.create(
            student=request.user,
            course=course,
            completed_lessons=0,
            total_lessons=total_lessons,
            completion_percentage=0,
            xp_earned=0
        )

        log_activity(
            student=request.user,
            activity_type='COURSE_ENROLL',
            course=course
        )

    return redirect('student_dashboard')


# -------------------------
# MY COURSES
# -------------------------
@student_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user)

    certified_course_ids = set(
        Certificate.objects.filter(
            student=request.user,
            is_active=True
        ).values_list('course_id', flat=True)
    )

    return render(
        request,
        'students/my_courses.html',
        {
            'enrollments': enrollments,
            'certified_course_ids': certified_course_ids
        }
    )


# -------------------------
# LESSON LIST
# -------------------------
@student_required
def lesson_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not Enrollment.objects.filter(
        student=request.user,
        course=course
    ).exists():
        return redirect('student_dashboard')

    start_learning_session(
        student=request.user,
        course=course
    )

    lessons = Lesson.objects.filter(
        course=course,
        is_active=True
    ).order_by('order')

    progress = StudentProgress.objects.filter(
        student=request.user,
        course=course
    ).first()

    completed = progress.completed_lessons if progress else 0
    total = lessons.count()

    return render(
        request,
        'students/lessons.html',
        {
            'course': course,
            'lessons': lessons,
            'completed': completed,
            'total': total
        }
    )


# -------------------------
# LESSON DETAIL
# -------------------------
@student_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(
        Lesson,
        id=lesson_id,
        is_active=True
    )

    get_object_or_404(
        Enrollment,
        student=request.user,
        course=lesson.course
    )

    progress, _ = StudentProgress.objects.get_or_create(
        student=request.user,
        course=lesson.course
    )

    already_completed = LessonCompletion.objects.filter(
        student=request.user,
        lesson=lesson
    ).exists()

    if request.method == 'POST' and not already_completed:
        LessonCompletion.objects.create(
            student=request.user,
            lesson=lesson
        )

        completed_count = LessonCompletion.objects.filter(
            student=request.user,
            lesson__course=lesson.course
        ).count()

        total_lessons = Lesson.objects.filter(
            course=lesson.course,
            is_active=True
        ).count()

        progress.completed_lessons = completed_count
        progress.total_lessons = total_lessons

        if total_lessons > 0:
            progress.completion_percentage = min(
                round((completed_count / total_lessons) * 100, 2),
                100
            )
        else:
            progress.completion_percentage = 0

        progress.xp_earned += 10
        progress.last_updated = now()
        progress.save()

        if progress.completion_percentage == 100:
            Certificate.objects.get_or_create(
                student=request.user,
                course=lesson.course,
                defaults={
                    'certificate_id': f"CERT-{uuid.uuid4().hex[:12].upper()}"
                }
            )

        log_activity(
            student=request.user,
            activity_type='LESSON_VIEW',
            course=lesson.course,
            metadata={
                'lesson_title': lesson.title
            }
        )

        check_and_award_achievements(request.user)

        update_student_skills(
            student=request.user,
            course=lesson.course,
            base_points=5
        )

        today = localdate()
        streak, _ = LearningStreak.objects.get_or_create(student=request.user)

        if streak.last_activity_date == today:
            pass
        elif streak.last_activity_date == today - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1

        streak.last_activity_date = today
        streak.longest_streak = max(
            streak.longest_streak,
            streak.current_streak
        )
        streak.save()

        check_and_award_streak_rewards(
            request.user,
            streak.current_streak
        )

        end_learning_session(
            student=request.user,
            course=lesson.course
        )

        redirect_url = reverse('student_lesson_list', args=[lesson.course.id])
        return redirect(f"{redirect_url}?lesson_completed={lesson.id}")

    return render(
        request,
        'students/lesson_detail.html',
        {
            'lesson': lesson,
            'progress': progress,
            'already_completed': already_completed
        }
    )


# -------------------------
# VIEW CERTIFICATE
# -------------------------
@student_required
def view_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    certificate = get_object_or_404(
        Certificate,
        student=request.user,
        course=course,
        is_active=True
    )

    return render(
        request,
        'students/certificate.html',
        {
            'certificate': certificate,
            'course': course,
            'student': request.user,
            'logo_url': request.build_absolute_uri(static('images/logo.png')),
            'seal_url': request.build_absolute_uri(static('images/seal.png')),
        }
    )


# -------------------------
# DOWNLOAD CERTIFICATE PDF
# -------------------------
@student_required
def download_certificate_pdf(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    certificate = get_object_or_404(
        Certificate,
        student=request.user,
        course=course,
        is_active=True
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename=certificate_{course.id}.pdf'
    )

    width, height = landscape(A4)
    c = canvas.Canvas(response, pagesize=(width, height))

    blue = HexColor("#1f4fd8")
    green = HexColor("#2e7d32")

    # BORDER
    c.setStrokeColor(blue)
    c.setLineWidth(4)
    c.rect(30, 30, width - 60, height - 60)

    # TITLE
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(blue)
    c.drawCentredString(width / 2, height - 100, "Certificate of Completion")

    # SUBTITLE
    c.setFont("Helvetica", 16)
    c.setFillColor(HexColor("#000000"))
    c.drawCentredString(width / 2, height - 160, "This is to certify that")

    # STUDENT NAME
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(
        width / 2,
        height - 210,
        request.user.get_full_name() or request.user.username
    )

    # TEXT
    c.setFont("Helvetica", 16)
    c.drawCentredString(
        width / 2,
        height - 260,
        "has successfully completed the course"
    )

    # COURSE NAME
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(green)
    c.drawCentredString(
        width / 2,
        height - 310,
        course.title
    )

    # DESCRIPTION
    c.setFont("Helvetica", 14)
    c.setFillColor(HexColor("#000000"))
    c.drawCentredString(
        width / 2,
        height - 360,
        "The student has demonstrated the required knowledge and skills"
    )

    # FOOTER
    c.setFont("Helvetica", 12)
    c.drawString(80, 120, f"Certificate ID: {certificate.certificate_id}")
    c.drawString(
        80, 95,
        f"Instructor: {course.instructor.get_full_name() if course.instructor else '—'}"
    )
    c.drawRightString(width - 80, 120, f"Issued On: {certificate.issued_at.strftime('%d %b %Y')}")
    c.drawRightString(width - 80, 95, "Platform: Craftlanee")

    c.showPage()
    c.save()

    return response


# -------------------------
# STUDENT ACHIEVEMENTS
# -------------------------
@student_required
def student_achievements(request):
    achievements = StudentAchievement.objects.filter(
        student=request.user
    ).select_related('achievement')

    return render(
        request,
        'students/achievements.html',
        {
            'achievements': achievements
        }
    )


# -------------------------
# STUDENT LEADERBOARD
# -------------------------
@student_required
def student_leaderboard(request):
    leaderboard = (
        StudentProgress.objects
        .values('student__username', 'student_id')
        .annotate(total_xp=Sum('xp_earned'))
        .order_by('-total_xp')
    )

    streak_map = {
        s.student_id: s
        for s in LearningStreak.objects.all()
    }

    ranked = []
    rank = 1

    for entry in leaderboard:
        streak = streak_map.get(entry['student_id'])
        ranked.append({
            'rank': rank,
            'username': entry['student__username'],
            'xp': entry['total_xp'],
            'current_streak': streak.current_streak if streak else 0,
            'longest_streak': streak.longest_streak if streak else 0
        })
        rank += 1

    return render(
        request,
        'students/leaderboard.html',
        {
            'leaderboard': ranked
        }
    )


# -------------------------
# STUDENT QUIZ LIST
# -------------------------
@student_required
def student_quiz_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    get_object_or_404(
        Enrollment,
        student=request.user,
        course=course
    )

    quizzes = Quiz.objects.filter(
        course=course,
        is_active=True
    )

    attempts = {
        a.quiz_id: a
        for a in StudentQuizAttempt.objects.filter(
            student=request.user,
            quiz__course=course
        )
    }

    return render(
        request,
        'students/quizzes.html',
        {
            'course': course,
            'quizzes': quizzes,
            'attempts': attempts
        }
    )


# -------------------------
# ATTEMPT QUIZ
# -------------------------
@student_required
def attempt_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)

    get_object_or_404(
        Enrollment,
        student=request.user,
        course=quiz.course
    )

    start_learning_session(
        student=request.user,
        course=quiz.course
    )

    attempt = StudentQuizAttempt.objects.filter(
        student=request.user,
        quiz=quiz
    ).first()

    if attempt and attempt.passed:
        return redirect('student_quiz_list', course_id=quiz.course.id)

    questions = quiz.questions.all()

    if request.method == 'POST':
        score = 0
        per_question = quiz.total_marks // questions.count()

        for q in questions:
            selected = request.POST.get(str(q.id))
            if selected == q.correct_option:
                score += per_question

        passed = score >= quiz.pass_mark

        StudentQuizAttempt.objects.update_or_create(
            student=request.user,
            quiz=quiz,
            defaults={
                'score': score,
                'passed': passed
            }
        )

        log_activity(
            student=request.user,
            activity_type='QUIZ_ATTEMPT',
            course=quiz.course,
            metadata={
                'quiz': quiz.title,
                'score': score,
                'passed': passed
            }
        )

        if passed:
            progress = StudentProgress.objects.get(
                student=request.user,
                course=quiz.course
            )

            quiz_xp = quiz.pass_mark // 2
            progress.xp_earned += quiz_xp
            progress.last_updated = now()
            progress.save()

            update_student_skills(
                student=request.user,
                course=quiz.course,
                earned_xp=quiz_xp
            )

            check_and_award_achievements(request.user)

        end_learning_session(
            student=request.user,
            course=quiz.course
        )

        redirect_url = reverse('student_quiz_list', args=[quiz.course.id])
        return redirect(f"{redirect_url}?just_attempted={quiz.id}&passed={int(passed)}")

    return render(
        request,
        'students/attempt_quiz.html',
        {
            'quiz': quiz,
            'questions': questions
        }
    )


# -------------------------
# STREAK REWARDS
# -------------------------
@student_required
def streak_rewards(request):
    streak = LearningStreak.objects.filter(
        student=request.user
    ).first()

    rewards = StreakReward.objects.filter(is_active=True).order_by('streak_days')

    earned = ActivityLog.objects.filter(
        student=request.user,
        activity_type='STREAK_REWARD'
    )

    earned_days = {
        log.metadata.get('streak_days')
        for log in earned if log.metadata
    }

    return render(
        request,
        'students/streak_rewards.html',
        {
            'streak': streak,
            'rewards': rewards,
            'earned_days': earned_days
        }
    )


# -------------------------
# STUDENT SKILLS
# -------------------------
@student_required
def student_skills(request):
    skills = StudentSkill.objects.filter(student=request.user)

    return render(
        request,
        'students/skills.html',
        {
            'skills': skills
        }
    )


# -------------------------
# ACTIVITY TIMELINE
# -------------------------
@student_required
def activity_timeline(request):
    activities = ActivityLog.objects.filter(
        student=request.user
    ).order_by('-timestamp')[:100]

    return render(
        request,
        'students/activity_timeline.html',
        {
            'activities': activities
        }
    )


# -------------------------
# AI LEARNING PATH
# -------------------------
@student_required
def ai_learning_path(request):
    suggestions = []
    role = None

    if request.method == "POST":
        role = request.POST.get("role", "").strip()

        if role:
            suggestions = generate_ai_learning_path(
                student=request.user,
                role=role
            )

            AILearningPathQuery.objects.create(
                student=request.user,
                role=role,
                suggestions=suggestions
            )

    history = AILearningPathQuery.objects.filter(
        student=request.user
    ).order_by('-created_at')[:50]

    return render(
        request,
        'students/ai_learning_path.html',
        {
            'role': role,
            'suggestions': suggestions,
            'history': history,
        }
    )