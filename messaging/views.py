from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from adminpanel.decorators import admin_required

from .models import Broadcast, BroadcastRecipient
from .services import create_broadcast


@login_required
@admin_required
def admin_broadcast_list(request):
    broadcasts = Broadcast.objects.select_related('sender').all()

    q = request.GET.get('q', '').strip()
    if q:
        broadcasts = broadcasts.filter(subject__icontains=q) | broadcasts.filter(message__icontains=q)

    recipient = request.GET.get('recipient', '')
    if recipient:
        broadcasts = broadcasts.filter(recipient_type=recipient)

    priority = request.GET.get('priority', '')
    if priority:
        broadcasts = broadcasts.filter(priority=priority)

    broadcasts = broadcasts.distinct()

    rows = []
    for broadcast in broadcasts:
        total = broadcast.recipients.count()
        read = broadcast.recipients.filter(is_read=True).count()
        rows.append({'broadcast': broadcast, 'total': total, 'read': read})

    return render(request, 'messaging/admin_list.html', {
        'rows': rows,
        'q': q,
        'recipient': recipient,
        'priority': priority,
        'recipient_choices': Broadcast.RECIPIENT_CHOICES,
        'priority_choices': Broadcast.PRIORITY_CHOICES,
    })


@login_required
@admin_required
def admin_broadcast_create(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        priority = request.POST.get('priority', 'NORMAL')
        recipient_type = request.POST.get('recipient_type', 'EVERYONE')
        attachment = request.FILES.get('attachment')

        if not subject or not message:
            messages.error(request, "Subject and message are required.")
            return redirect('admin_broadcast_create')

        create_broadcast(
            sender=request.user,
            subject=subject,
            message=message,
            priority=priority,
            recipient_type=recipient_type,
            attachment=attachment,
        )
        messages.success(request, "Broadcast sent.")
        return redirect('admin_broadcast_list')

    return render(request, 'messaging/admin_create.html', {
        'recipient_choices': Broadcast.RECIPIENT_CHOICES,
        'priority_choices': Broadcast.PRIORITY_CHOICES,
    })


@login_required
@admin_required
def admin_broadcast_detail(request, pk):
    broadcast = get_object_or_404(Broadcast.objects.select_related('sender'), pk=pk)
    recipients = broadcast.recipients.select_related('user').all()
    return render(request, 'messaging/admin_detail.html', {
        'broadcast': broadcast,
        'recipients': recipients,
    })


@login_required
@admin_required
def admin_broadcast_delete(request, pk):
    broadcast = get_object_or_404(Broadcast, pk=pk)
    if request.method == 'POST':
        broadcast.delete()
        messages.success(request, "Broadcast deleted.")
    return redirect('admin_broadcast_list')


def _require_inbox_role(request):
    profile = getattr(request.user, 'profile', None)
    return profile is not None and profile.role in ('STUDENT', 'INSTRUCTOR')


@login_required
def broadcast_inbox(request):
    if not _require_inbox_role(request):
        messages.error(request, "Access denied.")
        return redirect('login')

    role = request.user.profile.role
    template_name = (
        'messaging/inbox_student.html' if role == 'STUDENT' else 'messaging/inbox_instructor.html'
    )

    entries = BroadcastRecipient.objects.filter(user=request.user).select_related('broadcast', 'broadcast__sender')

    q = request.GET.get('q', '').strip()
    if q:
        entries = entries.filter(broadcast__subject__icontains=q) | entries.filter(broadcast__message__icontains=q)
        entries = entries.distinct()

    filter_by = request.GET.get('filter', 'all')
    if filter_by == 'unread':
        entries = entries.filter(is_read=False)
    elif filter_by == 'read':
        entries = entries.filter(is_read=True)
    elif filter_by == 'important':
        entries = entries.filter(broadcast__priority__in=('IMPORTANT', 'URGENT'))

    return render(request, template_name, {
        'entries': entries,
        'q': q,
        'filter_by': filter_by,
        'unread_count': BroadcastRecipient.objects.filter(user=request.user, is_read=False).count(),
    })


@login_required
def broadcast_mark_read(request, pk):
    if not _require_inbox_role(request):
        return JsonResponse({'error': 'forbidden'}, status=403)

    entry = get_object_or_404(BroadcastRecipient, pk=pk, user=request.user)
    if request.method == 'POST' and not entry.is_read:
        entry.is_read = True
        entry.read_at = timezone.now()
        entry.save(update_fields=['is_read', 'read_at'])

    return JsonResponse({
        'is_read': entry.is_read,
        'unread_count': BroadcastRecipient.objects.filter(user=request.user, is_read=False).count(),
    })


@login_required
def broadcast_unread_count(request):
    if not _require_inbox_role(request):
        return JsonResponse({'unread_count': 0, 'latest': None})

    qs = BroadcastRecipient.objects.filter(user=request.user, is_read=False).select_related(
        'broadcast', 'broadcast__sender'
    )
    unread_count = qs.count()
    latest_entry = qs.first()
    latest = None
    if latest_entry:
        latest = {
            'subject': latest_entry.broadcast.subject,
            'sender': latest_entry.broadcast.sender.get_full_name() or latest_entry.broadcast.sender.username,
            'priority': latest_entry.broadcast.priority,
        }

    return JsonResponse({'unread_count': unread_count, 'latest': latest})
