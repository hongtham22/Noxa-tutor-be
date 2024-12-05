# asgi.py
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "noxa_be.settings")
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
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