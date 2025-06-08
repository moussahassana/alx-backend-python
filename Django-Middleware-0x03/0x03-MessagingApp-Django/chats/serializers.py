from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = User
        fields = [
            "user_id", "username", "first_name", "last_name", "email",
            "bio", "phone_number", "profile_picture", "last_seen"
        ]

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField()
    sent_at = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "message_id", "sender", "message_body", "sent_at", "conversation"
        ]

    def get_sent_at(self, obj):
        return obj.sent_at.strftime("%Y-%m-%d %H:%M:%S")

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id", "participants", "created_at", "messages"
        ]

    def get_messages(self, obj):
        messages = obj.messages.all()
        return MessageSerializer(messages, many=True).data

    def validate(self, data):
        if not data.get('participants'):
            raise serializers.ValidationError("A conversation must have at least one participant.")
        return data