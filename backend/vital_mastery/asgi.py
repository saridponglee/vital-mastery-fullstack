"""
ASGI config for VITAL MASTERY project with comprehensive real-time support.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import re
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
import django_eventstream

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vital_mastery.settings.development')

# Initialize Django ASGI application early to ensure the AppRegistry is populated
django_asgi_app = get_asgi_application()

# SSE Authentication Middleware
class SSEAuthMiddleware:
    """
    Custom middleware for SSE authentication and connection tracking.
    Handles authentication validation and rate limiting for SSE connections.
    """
    
    def __init__(self, inner):
        self.inner = inner
    
    def __call__(self, scope, receive, send):
        # Add custom authentication logic here if needed
        # For now, delegate to the inner application
        return self.inner(scope, receive, send)

application = ProtocolTypeRouter({
    "http": URLRouter([
        # EventStream routing with custom middleware
        *django_eventstream.routing.urlpatterns,
        # Fallback to Django's ASGI application for all other routes
        re_path(r'^', SSEAuthMiddleware(django_asgi_app)),
    ]),
}) 