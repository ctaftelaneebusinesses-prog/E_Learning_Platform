from django.contrib.auth.models import User
from django.db import models


class Broadcast(models.Model):
    RECIPIENT_CHOICES = (
        ('STUDENTS', 'All Students'),
        ('INSTRUCTORS', 'All Instructors'),
        ('EVERYONE', 'Everyone'),
    )

    PRIORITY_CHOICES = (
        ('NORMAL', 'Normal'),
        ('IMPORTANT', 'Important'),
        ('URGENT', 'Urgent'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_broadcasts')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='NORMAL')
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_CHOICES)
    attachment = models.FileField(upload_to='broadcast_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} ({self.get_recipient_type_display()})"


class BroadcastRecipient(models.Model):
    broadcast = models.ForeignKey(Broadcast, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='broadcast_messages')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('broadcast', 'user')
        ordering = ['-broadcast__created_at']

    def __str__(self):
        return f"{self.user.username} <- {self.broadcast.subject}"
