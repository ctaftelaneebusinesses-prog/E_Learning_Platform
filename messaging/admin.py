from django.contrib import admin

from .models import Broadcast, BroadcastRecipient


class BroadcastRecipientInline(admin.TabularInline):
    model = BroadcastRecipient
    extra = 0
    readonly_fields = ('user', 'is_read', 'read_at')
    can_delete = False


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ('subject', 'recipient_type', 'priority', 'sender', 'created_at')
    list_filter = ('recipient_type', 'priority')
    search_fields = ('subject', 'message')
    inlines = [BroadcastRecipientInline]


@admin.register(BroadcastRecipient)
class BroadcastRecipientAdmin(admin.ModelAdmin):
    list_display = ('broadcast', 'user', 'is_read', 'read_at')
    list_filter = ('is_read',)
