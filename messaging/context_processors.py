from .models import BroadcastRecipient


def broadcast_unread(request):
    if not request.user.is_authenticated:
        return {}

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in ('STUDENT', 'INSTRUCTOR'):
        return {}

    return {
        'broadcast_unread_count': BroadcastRecipient.objects.filter(
            user=request.user, is_read=False
        ).count()
    }
