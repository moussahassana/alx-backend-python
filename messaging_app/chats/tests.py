from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from chats.models import Conversation, Message

User = get_user_model()

class MessagingAppTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1', email='user1@example.com', password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2', email='user2@example.com', password='testpass123'
        )
        self.superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )

        self.conversation = Conversation.objects.create()
        self.conversation.participants.set([self.user1, self.user2])

        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            message_body='Hello, user2!'
        )

        self.user1_token = self._get_jwt_token(self.user1)
        self.user2_token = self._get_jwt_token(self.user2)
        self.superuser_token = self._get_jwt_token(self.superuser)

    def _get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_user_can_access_own_conversations(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('conversation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['conversation_id'], str(self.conversation.conversation_id))

    def test_non_participant_cannot_access_conversation(self):
        non_participant = User.objects.create_user(
            username='user3', email='user3@example.com', password='testpass123'
        )
        non_participant_token = self._get_jwt_token(non_participant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {non_participant_token}')
        url = reverse('conversation-detail', kwargs={'pk': str(self.conversation.conversation_id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_access_all_conversations(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.superuser_token}')
        url = reverse('conversation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_conversation(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('conversation-list')
        data = {'participants': [str(self.user2.user_id)]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(str(self.user1.user_id), [p['user_id'] for p in response.data['participants']])
        self.assertIn(str(self.user2.user_id), [p['user_id'] for p in response.data['participants']])

    def test_create_conversation_without_participants(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('conversation-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_user_can_send_message(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('conversation-messages-list', kwargs={'conversation_pk': str(self.conversation.conversation_id)})
        data = {
            'conversation': str(self.conversation.conversation_id),
            'message_body': 'Test message'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message_body'], 'Test message')
        self.assertEqual(response.data['sender']['user_id'], str(self.user1.user_id))

    def test_non_participant_cannot_send_message(self):
        non_participant = User.objects.create_user(
            username='user3', email='user3@example.com', password='testpass123'
        )
        non_participant_token = self._get_jwt_token(non_participant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {non_participant_token}')
        url = reverse('conversation-messages-list', kwargs={'conversation_pk': str(self.conversation.conversation_id)})
        data = {
            'conversation': str(self.conversation.conversation_id),
            'message_body': 'Unauthorized message'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_only_update_own_message(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('conversation-messages-detail', kwargs={
            'conversation_pk': str(self.conversation.conversation_id),
            'pk': str(self.message.message_id)
        })
        data = {'message_body': 'Updated message'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message_body'], 'Updated message')

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user2_token}')
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access(self):
        self.client.credentials()
        url = reverse('conversation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_authentication(self):
        url = reverse('token_obtain_pair')
        data = {'username': 'user1', 'password': 'testpass123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        url = reverse('conversation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_message_pagination(self):
        # Create 25 messages to test pagination (20 per page)
        for i in range(25):
            Message.objects.create(
                conversation=self.conversation,
                sender=self.user1,
                message_body=f"Message {i}"
            )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('conversation-messages-list', kwargs={'conversation_pk': str(self.conversation.conversation_id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 20)  # Check page size
        self.assertIn('next', response.data)  # Check for next page

    def test_message_filter_by_sender(self):
        # Create a message by user2
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            message_body="User2's message"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('conversation-messages-list', kwargs={'conversation_pk': str(self.conversation.conversation_id)})
        response = self.client.get(url, {'sender': str(self.user2.user_id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['sender']['user_id'], str(self.user2.user_id))