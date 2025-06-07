from rest_framework import permissions

class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to read/write it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow all actions for superusers
        if request.user and request.user.is_superuser:
            return True

        return request.user in obj.participants.all()


class IsSenderOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the sender of a message to update/delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow all actions for superusers
        if request.user and request.user.is_superuser:
            return True

        return obj.sender == request.user
