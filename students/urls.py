from django.urls import path
from . import views
from .views import (
    ai_learning_path,
    attempt_quiz,
    download_certificate_pdf,
    lesson_detail,
    lesson_list,
    student_achievements,
    student_dashboard,
    course_catalog,
    enroll_course,
    my_courses,
    student_leaderboard,
    student_quiz_list,
    student_skills,
    view_certificate,
    

)

urlpatterns = [
    path('dashboard/', student_dashboard, name='student_dashboard'),
    path('courses/', course_catalog, name='student_course_list'),
    path('courses/enroll/<int:course_id>/', enroll_course, name='enroll_course'),
    path('my-courses/', my_courses, name='student_my_courses'),
    path(
        'courses/<int:course_id>/lessons/',
        lesson_list,
        name='student_lesson_list'
    ),
    path(
        'lessons/<int:lesson_id>/',
        lesson_detail,
        name='student_lesson_detail'
    ),
    path(
        'achievements/',
        student_achievements,
        name='student_achievements'
    ),
    path(
        'leaderboard/',
        student_leaderboard,
        name='student_leaderboard'
    ),
    path(
        'courses/<int:course_id>/quizzes/',
        student_quiz_list,
        name='student_quiz_list'
    ),

    path(
        'quizzes/<int:quiz_id>/attempt/',
        attempt_quiz,
        name='attempt_quiz'
    ),
    path(
        'streak-rewards/',
        views.streak_rewards,
        name='student_streak_rewards'
    ),
    path('skills/', student_skills, name='student_skills'),
    path('activity/', views.activity_timeline, name='student_activity'),
    path(
        'ai-learning-path/',
        views.ai_learning_path,
        name='ai_learning_path'
    ),
    path(
        'certificate/<int:course_id>/',
        view_certificate,
        name='student_view_certificate'
    ),
    path(
        'certificate/<int:course_id>/download/',
        download_certificate_pdf,
        name='student_download_certificate'
    ),



]
