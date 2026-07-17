from django.urls import path
from .views import achievement_list, course_list, create_achievement, create_course, create_skill, create_streak_reward, map_course_skill, progress_overview, skill_list, streak_overview, time_tracking_overview, toggle_achievement_status, toggle_course_status
from .views import lesson_list, create_lesson, toggle_lesson_status, question_list, create_question
from .views import revoke_certificate, reissue_certificate
from .views import certificate_list
from .views import user_activity_log, download_user_activity_log, live_user_activity_log, backfill_user_activity_log, sync_user_activity_log


from .views import (
    admin_dashboard,
    user_list,
    create_admin_user,
    update_user_role,
    toggle_user_status,
    pending_approvals,
    approve_user,
    reject_user,
    user_profile_detail,
    update_user_profile_detail,
    delete_user_account,
    quiz_list,
    create_quiz,
    toggle_quiz_status
)

urlpatterns = [
    path('', admin_dashboard, name='admin_dashboard'),
    path('users/', user_list, name='admin_user_list'),
    path('users/pending/', pending_approvals, name='admin_pending_approvals'),
    path('users/create/', create_admin_user, name='admin_create_user'),
    path('users/<int:user_id>/', user_profile_detail, name='admin_user_profile_detail'),
    path('users/<int:user_id>/update/', update_user_profile_detail, name='admin_update_user_profile_detail'),
    path('users/<int:user_id>/delete/', delete_user_account, name='admin_delete_user_account'),
    path('users/role/<int:user_id>/', update_user_role, name='update_user_role'),
    path('users/status/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/approve/', approve_user, name='admin_approve_user'),
    path('users/<int:user_id>/reject/', reject_user, name='admin_reject_user'),
    path('courses/', course_list, name='admin_course_list'),
    path('courses/create/', create_course, name='admin_create_course'),
    path('courses/status/<int:course_id>/', toggle_course_status, name='toggle_course_status'),
    path('courses/<int:course_id>/lessons/', lesson_list, name='admin_lesson_list'),
    path('courses/<int:course_id>/lessons/create/', create_lesson, name='admin_create_lesson'),
    path('lessons/status/<int:lesson_id>/', toggle_lesson_status, name='toggle_lesson_status'),
    path('courses/<int:course_id>/quizzes/', quiz_list, name='admin_quiz_list'),
    path('courses/<int:course_id>/quizzes/create/', create_quiz, name='admin_create_quiz'),
    path('quizzes/status/<int:quiz_id>/', toggle_quiz_status, name='toggle_quiz_status'),
    path('quizzes/<int:quiz_id>/questions/', question_list, name='admin_question_list'),
    path('quizzes/<int:quiz_id>/questions/create/', create_question, name='admin_create_question'),
    path('progress/', progress_overview, name='admin_progress'),
    path('achievements/', achievement_list, name='admin_achievement_list'),
    path('achievements/create/', create_achievement, name='admin_create_achievement'),
    path('achievements/status/<int:achievement_id>/', toggle_achievement_status, name='toggle_achievement_status'),
    path('streaks/', streak_overview, name='admin_streaks'),
    path('streaks/reward/create/', create_streak_reward, name='admin_create_streak_reward'),
    path('skills/', skill_list, name='admin_skill_list'),
    path('skills/create/', create_skill, name='admin_create_skill'),
    path('skills/map/', map_course_skill, name='admin_map_course_skill'),
    path('time-tracking/', time_tracking_overview, name='admin_time_tracking'),
    path(
        'certificates/revoke/<int:certificate_id>/',
        revoke_certificate,
        name='admin_revoke_certificate'
    ),
    path(
        'certificates/reissue/<int:certificate_id>/',
        reissue_certificate,
        name='admin_reissue_certificate'
    ),
    path(
        'certificates/',
        certificate_list,
        name='admin_certificate_list'
    ),
    path('activity-log/', user_activity_log, name='admin_user_activity_log'),
    path('activity-log/download/', download_user_activity_log, name='admin_download_user_activity_log'),
    path('activity-log/live/', live_user_activity_log, name='admin_live_user_activity_log'),
    path('activity-log/backfill/', backfill_user_activity_log, name='admin_backfill_user_activity_log'),
    path('activity-log/sync/', sync_user_activity_log, name='admin_sync_user_activity_log'),


]
