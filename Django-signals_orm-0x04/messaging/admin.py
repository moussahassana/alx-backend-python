from django.contrib import admin
from .models import Message, Notification, MessageHistory

class MessageHistoryInline(admin.TabularInline):
    """Allows viewing of edit history directly within the Message admin page."""
    model = MessageHistory
    extra = 0 # Don't show extra empty forms
    readonly_fields = ('old_content', 'edited_by', 'edited_at')
    can_delete = False
    verbose_name = "Message Edit History"
    verbose_name_plural = "Message Edit History"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'is_edited', 'timestamp')
    list_filter = ('sender', 'receiver', 'is_edited')
    search_fields = ('content',)
    readonly_fields = ('timestamp',)
    inlines = [MessageHistoryInline] # Add the inline history view

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'timestamp')
    list_filter = ('is_read', 'user')

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'old_content', 'edited_by', 'edited_at')
    readonly_fields = ('message', 'old_content', 'edited_by', 'edited_at')
