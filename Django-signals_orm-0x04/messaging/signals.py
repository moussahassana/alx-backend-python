# messaging/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

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
