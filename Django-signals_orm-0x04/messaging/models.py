from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Prefetch

class ThreadManager(models.Manager):
    def get_thread(self, message_id):
        """
        Fetches a message and all its replies, optimized to prevent N+1 queries.
        This demonstrates the use of select_related and prefetch_related.
        """
        # We start with the top-level message
        # select_related is used for foreign key relationships (sender, receiver, parent_message).
        # It performs a SQL JOIN.
        queryset = self.get_queryset().select_related(
            'sender', 'receiver', 'parent_message'
        )

        # prefetch_related is used for reverse foreign keys or many-to-many.
        # It performs a separate lookup and joins the data in Python.
        # This is ideal for fetching all replies recursively.
        # We also prefetch the sender/receiver for the replies.
        queryset = queryset.prefetch_related(
            Prefetch(
                'replies',
                queryset=Message.objects.select_related('sender', 'receiver').prefetch_related(
                    Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver'))
                    # This can be nested further for deeper threads
                )
            ),
            'edit_history'
        )
        
        try:
            # Get the root message of the thread
            root_message = queryset.get(pk=message_id, parent_message=None)
            return root_message
        except self.model.DoesNotExist:
            return None


class Message(models.Model):
    """
    Represents a message sent from one user to another.
    Can be a top-level message or a reply to another message.
    """
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    
    # Self-referential ForeignKey for threaded conversations
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )

    # Add the custom manager
    objects = models.Manager() # The default manager
    threads = ThreadManager() # Our custom manager for fetching threads

    def __str__(self):
        """String representation of a Message."""
        if self.parent_message:
            return f"Reply from {self.sender} to {self.receiver} on message {self.parent_message.id}"
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
    """
    message = models.ForeignKey(Message, related_name='edit_history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = "Message History"

    def __str__(self):
        """String representation of a MessageHistory entry."""
        return f"Edit for message {self.message.id} at {self.edited_at}"
