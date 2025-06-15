from django.contrib import admin
from .models import Message, Notification

# Register the Message model with the admin site
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp')
    list_filter = ('sender', 'receiver')
    search_fields = ('content',)

# Register the Notification model with the admin site
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'timestamp')
    list_filter = ('is_read', 'user')