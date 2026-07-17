from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from allauth.account.signals import user_signed_up
from students.utils import log_activity
from courses.models import LearningStreak
from utils.activity_logger import log_user_registration
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        role = 'ADMIN' if instance.is_superuser else 'STUDENT'
        approval_status = 'APPROVED' if instance.is_superuser else 'PENDING'
        Profile.objects.create(user=instance, role=role, approval_status=approval_status)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=User)
def create_learning_streak(sender, instance, created, **kwargs):
    if created:
        LearningStreak.objects.create(student=instance)

@receiver(user_logged_in)
def log_login(sender, user, request, **kwargs):
    log_activity(user, 'LOGIN')

@receiver(user_logged_out)
def log_logout(sender, user, request, **kwargs):
    log_activity(user, 'LOGOUT')

@receiver(user_signed_up)
def log_social_registration(sender, request, user, **kwargs):
    """Covers accounts created via allauth (e.g. Google sign-in) - register_view
    handles the local signup form's registration logging separately."""
    log_user_registration(user, request)