from django.core.management.base import BaseCommand
from chats.models import User, Conversation, Message
import uuid

class Command(BaseCommand):
    help = 'Seeds the database with initial test users, a conversation, and a message for the messaging app'

    def handle(self, *args, **kwargs):
        # Seed Users
        users = [
            {
                'username': 'user1',
                'email': 'user1@example.com',
                'password': 'testpass123',
            },
            {
                'username': 'user2',
                'email': 'user2@example.com',
                'password': 'testpass123',
            },
            {
                'username': 'user3',
                'email': 'user3@example.com',
                'password': 'testpass123',
            },
        ]

        created_users = {}
        for user_data in users:
            username = user_data['username']
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                self.stdout.write(
                    self.style.WARNING(f"User '{username}' already exists with user_id: {user.user_id}")
                )
            else:
                user = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    password=user_data['password']
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Created user '{username}' with user_id: {user.user_id}")
                )
            created_users[username] = user

        # Seed Conversation and Message
        if created_users.get('user1') and created_users.get('user2'):
            conversation_id = uuid.uuid4()  # Generate a fixed UUID for consistency
            conversation, created = Conversation.objects.get_or_create(
                conversation_id=conversation_id,
                defaults={'created_at': None}
            )
            if created:
                conversation.participants.add(created_users['user1'], created_users['user2'])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created conversation with conversation_id: {conversation.conversation_id} "
                        f"between user1 and user2"
                    )
                )
                # Seed a sample message
                message = Message.objects.create(
                    conversation=conversation,
                    sender=created_users['user1'],
                    message_body="Hello, user2! (Seeded message)"
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created message with message_id: {message.message_id} from user1"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Conversation with conversation_id: {conversation.conversation_id} already exists"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Data seeding completed. Update Postman environment with user_id values above."
            )
        )