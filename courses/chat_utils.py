import os

from django.utils import timezone

ONLINE_WINDOW_SECONDS = 60

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.webp')


def is_online(user):
    profile = getattr(user, 'profile', None)
    if not profile or not profile.last_seen:
        return False
    return (timezone.now() - profile.last_seen).total_seconds() < ONLINE_WINDOW_SECONDS


def mark_read(chat, viewer):
    return chat.messages.exclude(sender=viewer).filter(is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )


def tick_state(message, other_online):
    """Returns 'read' | 'delivered' | 'sent' for a message's own status row."""
    if message.is_read:
        return 'read'
    if other_online:
        return 'delivered'
    return 'sent'


def serialize_message(message, viewer, other_online=False):
    attachment_url = message.attachment.url if message.attachment else None
    attachment_name = os.path.basename(message.attachment.name) if message.attachment else None
    is_image = bool(attachment_name) and attachment_name.lower().endswith(IMAGE_EXTENSIONS)

    reactions = {}
    for r in message.reactions.all():
        reactions.setdefault(r.emoji, []).append(r.user.username)

    return {
        'id': message.id,
        'is_me': message.sender_id == viewer.id,
        'sender_name': message.sender.first_name or message.sender.username,
        'message': message.message,
        'attachment_url': attachment_url,
        'attachment_name': attachment_name,
        'is_image': is_image,
        'voice_note_url': message.voice_note.url if message.voice_note else None,
        'created_at': message.created_at.isoformat(),
        'time_display': timezone.localtime(message.created_at).strftime('%H:%M'),
        'tick_state': tick_state(message, other_online) if message.sender_id == viewer.id else None,
        'reactions': [
            {'emoji': emoji, 'users': users, 'count': len(users)}
            for emoji, users in reactions.items()
        ],
    }
