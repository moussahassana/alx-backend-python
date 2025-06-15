from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

class MessagingSignalTestCase(TestCase):
    """
    Test suite for testing the message notification signal.
    """
    def setUp(self):
        """
        Set up the necessary objects for the tests.
        This runs before each test method.
        """
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

    def test_notification_created_on_new_message(self):
        """
        Test that a notification is correctly created automatically
        when a new message is sent.
        """
        # Check that no notifications exist initially
        self.assertEqual(Notification.objects.count(), 0)

        # Create and save a new message from user1 to user2
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello, this is a test!"
        )

        # Verify that one notification has been created
        self.assertEqual(Notification.objects.count(), 1)

        # Verify the details of the created notification
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)

    def test_no_notification_on_message_update(self):
        """
        Test that a notification is NOT created when an existing
        message is updated (saved again).
        """
        # Create an initial message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Initial message"
        )
        # At this point, one notification should exist
        self.assertEqual(Notification.objects.count(), 1)

        # Update the message content and save it again
        message.content = "Updated message content"
        message.save()

        # Verify that no *new* notification was created. The count should still be 1.
        self.assertEqual(Notification.objects.count(), 1)
