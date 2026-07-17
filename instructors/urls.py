from django.urls import path
from .views import (
    instructor_analytics,
    instructor_course_students,
    instructor_dashboard,
    lesson_list,
    create_lesson,
    student_progress,
    toggle_lesson_status,
    quiz_list,
    create_quiz,
    toggle_quiz_status,
    question_list,
    create_question,
    delete_question,
    progress_overview,
    achievement_list,
    create_achievement,
    toggle_achievement_status,
    streak_overview,
    create_streak_reward,
    skill_list,
    create_skill,
    map_course_skill,
    time_tracking_overview,
    certificate_list,
    revoke_certificate,
    reissue_certificate,
)

urlpatterns = [
    # Dashboard
    path('dashboard/', instructor_dashboard, name='instructor_dashboard'),

    # Lesson management
    path(
        'courses/<int:course_id>/lessons/',
        lesson_list,
        name='instructor_lesson_list'
    ),
    path(
        'courses/<int:course_id>/lessons/create/',
        create_lesson,
        name='instructor_create_lesson'
    ),
    path(
        'lessons/status/<int:lesson_id>/',
        toggle_lesson_status,
        name='instructor_toggle_lesson_status'
    ),

    # Quiz management
    path(
        'courses/<int:course_id>/quizzes/',
        quiz_list,
        name='instructor_quiz_list'
    ),
    path(
        'courses/<int:course_id>/quizzes/create/',
        create_quiz,
        name='instructor_create_quiz'
    ),
    path(
        'quizzes/status/<int:quiz_id>/',
        toggle_quiz_status,
        name='instructor_toggle_quiz_status'
    ),

    # Question management
    path(
        'quizzes/<int:quiz_id>/questions/',
        question_list,
        name='instructor_question_list'
    ),
    path(
        'quizzes/<int:quiz_id>/questions/create/',
        create_question,
        name='instructor_create_question'
    ),
    path(
        'questions/delete/<int:question_id>/',
        delete_question,
        name='instructor_delete_question'
    ),
    path(
        'courses/<int:course_id>/progress/',
        student_progress,
        name='instructor_student_progress'
    ),
    path(
        'analytics/',
        instructor_analytics,
        name='instructor_analytics'
    ),
    
    path(
        "courses/<int:course_id>/students/",
        instructor_course_students,
        name="instructor_course_students"
    ),

    # Admin-parity management sections
    path('progress/', progress_overview, name='instructor_progress'),

    path('achievements/', achievement_list, name='instructor_achievement_list'),
    path('achievements/create/', create_achievement, name='instructor_create_achievement'),
    path(
        'achievements/status/<int:achievement_id>/',
        toggle_achievement_status,
        name='instructor_toggle_achievement_status'
    ),

    path('streaks/', streak_overview, name='instructor_streaks'),
    path(
        'streaks/reward/create/',
        create_streak_reward,
        name='instructor_create_streak_reward'
    ),

    path('skills/', skill_list, name='instructor_skill_list'),
    path('skills/create/', create_skill, name='instructor_create_skill'),
    path('skills/map/', map_course_skill, name='instructor_map_course_skill'),

    path('time-tracking/', time_tracking_overview, name='instructor_time_tracking'),

    path('certificates/', certificate_list, name='instructor_certificate_list'),
    path(
        'certificates/revoke/<int:certificate_id>/',
        revoke_certificate,
        name='instructor_revoke_certificate'
    ),
    path(
        'certificates/reissue/<int:certificate_id>/',
        reissue_certificate,
        name='instructor_reissue_certificate'
    ),
]
