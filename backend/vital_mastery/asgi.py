"""
ASGI config for VITAL MASTERY project with real-time support.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import django_eventstream

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vital_mastery.settings.development')

# Initialize Django ASGI application early to ensure the AppRegistry is populated
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": URLRouter([
        # EventStream routing
        *django_eventstream.routing.urlpatterns,
        # Fallback to Django's ASGI application for all other routes
        re_path(r'^', django_asgi_app),
    ]),
})

# Import re for regex pattern
import re 