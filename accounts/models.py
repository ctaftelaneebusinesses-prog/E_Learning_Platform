from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('INSTRUCTOR', 'Instructor'),
        ('STUDENT', 'Student'),
    )

    APPROVAL_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    EDUCATION_TYPE_CHOICES = (
        ('SCHOOL', 'School (Classes 1-10)'),
        ('INTERMEDIATE', 'Intermediate (11-12)'),
        ('COLLEGE', 'College'),
        ('UNIVERSITY', 'University'),
        ('OTHER', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS_CHOICES, default='PENDING')

    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    skills = models.TextField(blank=True)

    education_type = models.CharField(max_length=20, choices=EDUCATION_TYPE_CHOICES, blank=True)
    profile_completed = models.BooleanField(default=False)

    phone_number = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    institution_name = models.CharField(max_length=255, blank=True)
    linkedin_url = models.URLField(max_length=300, blank=True)
    github_url = models.URLField(max_length=300, blank=True)

    last_seen = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username}: {self.message[:40]}"
