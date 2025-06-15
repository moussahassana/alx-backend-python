from django.db.models.signals import post_save, pre_save,pre_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory
from django.contrib.auth.models import User
import logging

# Set up a logger for debugging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    A signal that creates a Notification object automatically
    after a new Message instance is saved.
    
    Args:
        sender: The model class that sent the signal (Message).
        instance: The actual instance of the sender being saved.
        created (bool): True if a new record was created.
        **kwargs: Wildcard keyword arguments.
    """
    # Check if the message was just created
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    A signal that logs the old content of a message before it's updated
    and marks the message as edited. This runs *before* the model's save() method.
    """
    # We only want to act on updates, not new message creations.
    # An existing message will have a primary key (pk).
    if instance.pk:
        try:
            # Retrieve the original, unchanged message from the database.
            original_message = Message.objects.get(pk=instance.pk)
            
            # Compare the content to see if it has actually changed.
            if original_message.content != instance.content:
                # If the content is different, log the old version to MessageHistory.
                MessageHistory.objects.create(
                    message=original_message,
                    old_content=original_message.content
                )
                # Mark this message instance as edited. This change will be
                # saved when the pre_save signal handler finishes.
                instance.is_edited = True
        except Message.DoesNotExist:
            # This handles a rare edge case where the message might have been
            # deleted between the save() call and this signal running.
            pass

@receiver(pre_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    A signal that runs *before* a User is deleted.

    This signal is responsible for cleaning up all data related to the user
    to ensure the database is left in a clean state and to respect privacy.
    
    Args:
        sender: The model class that sent the signal (User).
        instance: The actual instance of the user being deleted.
        **kwargs: Wildcard keyword arguments.
    """
    print(f"Signal triggered: Deleting data for user {instance.username}")

    # Delete all messages where the user was the sender OR the receiver.
    # The MessageHistory related to these messages will be deleted automatically
    # due to the CASCADE setting on its own ForeignKey.
    Message.objects.filter(Q(sender=instance) | Q(receiver=instance)).delete()

    # Delete all notifications intended for the user.
    Notification.objects.filter(user=instance).delete()
    
    print(f"Cleanup complete for user {instance.username}")