from django.urls import path
from .views import (
    register_view,
    login_view,
    logout_view,
    dashboard_redirect,
    profile_view,
    complete_profile_view,
    api_get_profile,
    api_update_profile,
    api_upload_picture,
    api_change_password,
    notification_read,
    notifications_mark_all_read,
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('dashboard/', dashboard_redirect, name='dashboard'),

    path('profile/', profile_view, name='profile'),
    path('complete-profile/', complete_profile_view, name='complete_profile'),
    path('api/profile/', api_get_profile, name='api_get_profile'),
    path('api/profile/update/', api_update_profile, name='api_update_profile'),
    path('api/profile/upload-picture/', api_upload_picture, name='api_upload_picture'),
    path('api/profile/change-password/', api_change_password, name='api_change_password'),

    path('notifications/<int:pk>/read/', notification_read, name='notification_read'),
    path('notifications/mark-all-read/', notifications_mark_all_read, name='notifications_mark_all_read'),
]
