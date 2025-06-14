import logging
from datetime import datetime
import os
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