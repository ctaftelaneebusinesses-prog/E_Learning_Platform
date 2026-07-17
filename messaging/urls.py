from django.urls import path

from .views import (
    admin_broadcast_create,
    admin_broadcast_delete,
    admin_broadcast_detail,
    admin_broadcast_list,
    broadcast_inbox,
    broadcast_mark_read,
    broadcast_unread_count,
)

urlpatterns = [
    path('admin/', admin_broadcast_list, name='admin_broadcast_list'),
    path('admin/create/', admin_broadcast_create, name='admin_broadcast_create'),
    path('admin/<int:pk>/', admin_broadcast_detail, name='admin_broadcast_detail'),
    path('admin/<int:pk>/delete/', admin_broadcast_delete, name='admin_broadcast_delete'),

    path('inbox/', broadcast_inbox, name='broadcast_inbox'),
    path('inbox/<int:pk>/read/', broadcast_mark_read, name='broadcast_mark_read'),
    path('unread-count/', broadcast_unread_count, name='broadcast_unread_count'),
]
