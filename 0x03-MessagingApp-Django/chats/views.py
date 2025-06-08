from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation, IsSenderOrReadOnly
from .filters import MessageFilter
from .pagination import MessagePagination
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter]
    search_fields = ['participants__username', 'participants__email']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return Conversation.objects.all()
        if self.action == 'list':
            return Conversation.objects.filter(participants=user)
        return Conversation.objects.all()

    def create(self, request, *args, **kwargs):
        participants_ids = request.data.get('participants', [])
        if not participants_ids:
            return Response({"error": "Participants are required to create a conversation."},
                            status=status.HTTP_400_BAD_REQUEST)

        valid_users = User.objects.filter(user_id__in=participants_ids).count()
        if valid_users != len(participants_ids):
            return Response({"error": "One or more participant IDs are invalid."},
                            status=status.HTTP_400_BAD_REQUEST)

        if str(request.user.user_id) not in participants_ids:
            participants_ids.append(str(request.user.user_id))

        conversation = Conversation.objects.create()
        conversation.participants.set(participants_ids)
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsSenderOrReadOnly]
    pagination_class = MessagePagination  # Explicitly set pagination class
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['sender__username', 'message_body']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(conversation__participants=user)

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation')
        message_body = request.data.get('message_body')

        if not all([conversation_id, message_body]):
            return Response({"error": "Conversation and message_body are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id, participants=request.user)
        except Conversation.DoesNotExist:
            return Response({"error": "You are not a participant of this conversation."},
                            status=status.HTTP_403_FORBIDDEN)

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            message_body=message_body
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)