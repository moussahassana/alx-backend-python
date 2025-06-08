import logging
from datetime import datetime
import os
from django.core.cache import cache
from django.http import HttpResponseForbidden
parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Configure logger
logging.basicConfig(
    filename=os.path.join(parent_path, 'requests.log'),
    level=logging.INFO,
    format='%(message)s'
)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get user (authenticated or anonymous)
        user = request.user if request.user.is_authenticated else 'Anonymous'
        # Log the request
        logging.info(f"{datetime.now()} - User: {user} - Path: {request.path}")
        # Process the request and return response
        response = self.get_response(request)
        return response
    
class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get current server time
        current_hour = datetime.now().hour
        # Allow access only between 6 PM (18:00) and 9 PM (21:00)
        if not (18 <= current_hour < 21):
            return HttpResponseForbidden("Access to the messaging app is restricted outside 6 PM to 9 PM.")
        # Proceed with the request if within allowed hours
        response = self.get_response(request)
        return response
    
class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get client IP address
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        cache_key = f"messages:{ip_address}"

        # Time window: 60 seconds
        time_window = 60
        current_time = datetime.now()

        # Get existing timestamps from cache
        timestamps = cache.get(cache_key, [])
        # Filter timestamps within the 60-second window
        timestamps = [
            ts for ts in timestamps
            if (current_time - ts).total_seconds() <= time_window
        ]

        # Check if request is a POST (message sending)
        if request.method == 'POST':
            if len(timestamps) >= 5:
                return HttpResponseForbidden("You have exceeded the limit of 5 messages per minute.")
            # Add current timestamp
            timestamps.append(current_time)
            # Store updated timestamps with 60-second TTL
            cache.set(cache_key, timestamps, time_window)

        # Proceed with the request
        response = self.get_response(request)
        return response
    
class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for unauthenticated users or non-restricted methods
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Restrict DELETE requests and specific POST requests
        if request.method == 'DELETE' or (
            request.method == 'POST' and 'messages' in request.path.lower()
        ):
            if not (request.user.is_staff or request.user.is_moderator):
                return HttpResponseForbidden(
                    "Only admins or moderators can perform this action."
                )

        # Proceed with the request
        response = self.get_response(request)
        return response