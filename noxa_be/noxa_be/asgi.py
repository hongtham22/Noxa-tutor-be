# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.apps import apps

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "noxa_be.settings")
django_asgi_app = get_asgi_application()

from notifications.jwtTokenMiddleware import UserIDMiddleware
import notifications.routing


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": UserIDMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                notifications.routing.websocket_urlpatterns
            )
        )
    ),
})