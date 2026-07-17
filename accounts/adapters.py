from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .notifications import notify


class AccountAdapter(DefaultAccountAdapter):
    def respond_user_inactive(self, request: HttpRequest, user) -> HttpResponse:
        approval_status = getattr(getattr(user, 'profile', None), 'approval_status', 'APPROVED')
        if approval_status == 'REJECTED':
            messages.error(
                request,
                "Your registration was rejected by an admin. Please contact support for details."
            )
        elif approval_status == 'PENDING':
            messages.error(
                request,
                "Your registration is awaiting admin approval. You'll be able to log in once it's approved."
            )
        return super().respond_user_inactive(request, user)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        sociallogin.user.is_active = False  # locked until an admin approves the registration
        user = super().save_user(request, sociallogin, form=form)

        for admin in User.objects.filter(profile__role='ADMIN'):
            notify(
                admin,
                f"New Student registration from {user.username} (Google sign-in) is awaiting approval.",
                link=reverse('admin_user_list'),
            )

        return user
