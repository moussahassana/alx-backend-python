from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

class MessagingSignalAndThreadTestCase(TestCase):
    """
    Test suite for message signals and threaded conversations.
    """
    def setUp(self):
        """Set up the necessary objects for the tests."""
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.user3 = User.objects.create_user(username='user3', password='password123')

    def test_notification_created_on_new_message(self):
        """Test that a notification is created for a new message."""
        self.assertEqual(Notification.objects.count(), 0)
        Message.objects.create(sender=self.user1, receiver=self.user2, content="Hello!")
        self.assertEqual(Notification.objects.count(), 1)

    def test_message_edit_history_created(self):
        """Test that editing a message logs its old content."""
        message = Message.objects.create(sender=self.user1, receiver=self.user2, content="Original.")
        self.assertEqual(MessageHistory.objects.count(), 0)
        message.content = "Edited."
        message.save()
        self.assertEqual(MessageHistory.objects.count(), 1)
        self.assertTrue(Message.objects.get(pk=message.pk).is_edited)

    def test_threaded_replies(self):
        """
        Test that messages can be replied to, creating a thread.
        """
        # A top-level message from user1 to user2
        parent_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="This is the first message."
        )
        self.assertIsNone(parent_message.parent_message)

        # user2 replies to user1
        reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="This is a reply.",
            parent_message=parent_message
        )
        self.assertEqual(reply1.parent_message, parent_message)

        # user1 replies to user2's reply
        reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="This is a reply to the reply.",
            parent_message=reply1
        )
        self.assertEqual(reply2.parent_message, reply1)
        
        # Check the replies relationship from the parent message
        self.assertEqual(parent_message.replies.count(), 1)
        self.assertEqual(parent_message.replies.first(), reply1)
        
        # A notification should be created for each message/reply
        self.assertEqual(Notification.objects.count(), 3)

    def test_get_thread_optimization(self):
        """
        Test the ThreadManager's get_thread method to ensure it uses
        select_related and prefetch_related efficiently.
        """
        parent_message = Message.objects.create(sender=self.user1, receiver=self.user2, content="Parent")
        reply1 = Message.objects.create(sender=self.user2, receiver=self.user1, content="Reply 1", parent_message=parent_message)
        reply2 = Message.objects.create(sender=self.user1, receiver=self.user2, content="Reply to Reply 1", parent_message=reply1)

        # Use Django's assertNumQueries to test database optimization
        with self.assertNumQueries(3): # Query for root msg, query for replies, query for replies-to-replies
            thread = Message.threads.get_thread(parent_message.id)
            self.assertEqual(thread, parent_message)
            # Accessing related objects should not trigger new queries
            self.assertEqual(thread.sender.username, 'user1')
            self.assertEqual(thread.replies.first().sender.username, 'user2')
            self.assertEqual(thread.replies.first().replies.first().sender.username, 'user1')

