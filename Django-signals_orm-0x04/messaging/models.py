from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Prefetch

class ThreadManager(models.Manager):
    def get_thread(self, message_id):
        """
        Fetches a message and all its replies recursively and efficiently.
        
        This method uses select_related for single-object foreign key relationships
        (sender, receiver) and prefetch_related for reverse relationships (replies).
        This combination is key to avoiding the N+1 query problem.
        """
        # Define the queryset for replies, pre-loading their sender/receiver info
        replies_queryset = self.get_queryset().select_related('sender', 'receiver')

        # We start with the top-level message queryset
        # and prefetch its replies. For each reply, we also want to prefetch *its* replies.
        # This nested prefetching is what allows us to retrieve multi-level threads efficiently.
        queryset = self.get_queryset().select_related(
            'sender', 'receiver'
        ).prefetch_related(
            Prefetch(
                'replies', # The related_name for the parent_message field
                queryset=replies_queryset.prefetch_related(
                    Prefetch('replies', queryset=replies_queryset) # Level 2 replies
                )
            )
        )
        
        try:
            # Fetch the root message of the thread (a message with no parent)
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
    
    # Self-referential ForeignKey to enable threaded conversations.
    # 'self' means the ForeignKey points to this same model.
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies' # This name is used in prefetch_related
    )

    # Add the managers
    objects = models.Manager() # Keep the default manager
    threads = ThreadManager()  # Our custom manager for fetching threads

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        if self.parent_message:
            return f"Reply from {self.sender} on message {self.parent_message.id}"
        return f"Message from {self.sender} to {self.receiver}"
    
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
