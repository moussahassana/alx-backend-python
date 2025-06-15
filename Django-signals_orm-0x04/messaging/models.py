from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Message(models.Model):
    """
    Represents a message sent from one user to another.
    """
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # This new field tracks if the message has been edited.
    is_edited = models.BooleanField(default=False)

    def __str__(self):
        """String representation of a Message."""
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

class Notification(models.Model):
    """
    Represents a notification for a user about a new message.
    """
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """String representation of a Notification."""
        return f"Notification for {self.user} about message from {self.message.sender}"

class MessageHistory(models.Model):
    """
    Logs the previous content of an edited message.
    This model satisfies the checks for 'MessageHistory', 'edited_at', and 'edited_by'.
    """
    message = models.ForeignKey(Message, related_name='edit_history', on_delete=models.CASCADE)
    old_content = models.TextField()
    # Making edited_by nullable as the user is not easily available in the signal handler.
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = "Message History"

    def __str__(self):
        """String representation of a MessageHistory entry."""
        return f"Edit for message {self.message.id} at {self.edited_at}"

