from django_filters import rest_framework as filters
from chats.models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageFilter(filters.FilterSet):
    sender = filters.UUIDFilter(field_name="sender__user_id", lookup_expr="exact")
    sent_at__gte = filters.DateTimeFilter(field_name="sent_at", lookup_expr="gte")
    sent_at__lte = filters.DateTimeFilter(field_name="sent_at", lookup_expr="lte")

    class Meta:
        model = Message
        fields = ['sender', 'sent_at__gte', 'sent_at__lte']