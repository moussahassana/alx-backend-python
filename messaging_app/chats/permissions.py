# messaging_app/chats/permissions.py
from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to read/write it.
    """
    def has_object_permission(self, request, view, obj):
        # Explicitly check if the user is authenticated
        if not request.user.is_authenticated:
            return False
        # Allow superusers full access
        if request.user.is_superuser:
            return True
        # Allow only participants to access the conversation
        return request.user in obj.participants.all()

class IsSenderOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the sender of a message to update/delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Explicitly check if the user is authenticated
        if not request.user.is_authenticated:
            return False
        # Allow superusers full access
        if request.user.is_superuser:   
            return True
        # Allow safe methods (GET, HEAD, OPTIONS) for participants
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.conversation.participants.all()
        # Restrict PUT, PATCH, DELETE to the sender only
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return obj.sender == request.user
        return False