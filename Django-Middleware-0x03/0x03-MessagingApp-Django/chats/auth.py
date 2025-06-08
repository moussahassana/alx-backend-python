from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication to handle user_id as the primary key.
    """
    def authenticate(self, request):
        try:
            user, validated_token = super().authenticate(request)
            if user and not user.is_active:
                raise AuthenticationFailed('User account is disabled.')
            return user, validated_token
        except Exception:
            raise AuthenticationFailed('Invalid token or user.')

def get_user_from_token(request):
    """
    Helper function to extract the authenticated user from a JWT token.
    """
    auth = CustomJWTAuthentication()
    user, _ = auth.authenticate(request)
    return user