from django.contrib.auth.models import User

from .models import Broadcast, BroadcastRecipient


def _recipients_for(recipient_type):
    if recipient_type == 'STUDENTS':
        return User.objects.filter(profile__role='STUDENT')
    if recipient_type == 'INSTRUCTORS':
        return User.objects.filter(profile__role='INSTRUCTOR')
    return User.objects.filter(profile__role__in=('STUDENT', 'INSTRUCTOR'))


def create_broadcast(sender, subject, message, priority, recipient_type, attachment=None):
    broadcast = Broadcast.objects.create(
        sender=sender,
        subject=subject,
        message=message,
        priority=priority,
        recipient_type=recipient_type,
        attachment=attachment,
    )

    users = _recipients_for(recipient_type)
    BroadcastRecipient.objects.bulk_create([
        BroadcastRecipient(broadcast=broadcast, user=user)
        for user in users
    ])

    return broadcast
