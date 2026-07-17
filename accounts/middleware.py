from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .models import Profile


class ProfileCompletionMiddleware:
    """Forces students to finish onboarding (incl. Education Type) before
    reaching any other page. See accounts.views.complete_profile_view."""

    ALLOWED_PATH_PREFIXES = (
        '/static/',
        '/media/',
        '/accounts/complete-profile/',
        '/accounts/logout/',
        '/accounts/api/profile/upload-picture/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if (
                profile
                and profile.role == 'STUDENT'
                and not profile.profile_completed
                and not request.path.startswith(self.ALLOWED_PATH_PREFIXES)
            ):
                return redirect(reverse('complete_profile'))

        return self.get_response(request)


class UpdateLastSeenMiddleware:
    """Stamps Profile.last_seen on authenticated requests, throttled to
    once per 20s per user, to drive lightweight chat presence ("online")."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile:
                now = timezone.now()
                if not profile.last_seen or (now - profile.last_seen).total_seconds() > 20:
                    Profile.objects.filter(pk=profile.pk).update(last_seen=now)

        return response
