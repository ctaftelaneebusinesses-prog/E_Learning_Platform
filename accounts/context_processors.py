def notifications(request):
    if not request.user.is_authenticated:
        return {}

    qs = request.user.notifications.all()
    return {
        'nav_notifications': qs[:8],
        'nav_unread_count': qs.filter(is_read=False).count(),
    }


def pending_approvals(request):
    if not request.user.is_authenticated:
        return {}

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'ADMIN':
        return {}

    from django.contrib.auth.models import User
    return {
        'pending_approval_count': User.objects.filter(profile__approval_status='PENDING').count()
    }


def theme(request):
    from .themes import get_theme

    if not request.user.is_authenticated:
        return {'active_theme': get_theme('OTHER')}

    profile = getattr(request.user, 'profile', None)
    education_type = profile.education_type if profile and profile.role == 'STUDENT' else 'OTHER'
    return {'active_theme': get_theme(education_type)}
