from django.contrib import admin
from .models import Message, Notification, MessageHistory

class MessageHistoryInline(admin.TabularInline):
    """Allows viewing of edit history directly within the Message admin page."""
    model = MessageHistory
    extra = 0
    readonly_fields = ('old_content', 'edited_by', 'edited_at')
    can_delete = False
    verbose_name = "Message Edit History"
    verbose_name_plural = "Message Edit History"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'parent_message', 'is_edited', 'timestamp')
    list_filter = ('sender', 'receiver', 'is_edited')
    search_fields = ('content',)
    readonly_fields = ('timestamp',)
    inlines = [MessageHistoryInline]
    
    # Make parent_message a raw_id_field for easier selection of the parent
    raw_id_fields = ('parent_message',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'timestamp')
    list_filter = ('is_read', 'user')

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'old_content', 'edited_by', 'edited_at')
    readonly_fields = ('message', 'old_content', 'edited_by', 'edited_at')
