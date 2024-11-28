from urllib.parse import parse_qs

from channels.middleware import BaseMiddleware

from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from accounts.models import User  # replace with your actual user model path

class UserIDMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Parse the user ID from the query string
        query_string = parse_qs(scope["query_string"].decode())
        user_id = query_string.get("user_id", [None])[0]

        # Default to AnonymousUser if user_id is not provided
        if user_id is None:
            scope["user"] = AnonymousUser()
        else:
            try:
                # Fetch the user by ID and attach to the scope
                user = await self.get_user_by_id(user_id)
                scope["user"] = user
            except User.DoesNotExist:
                # Close the WebSocket connection if the user does not exist
                await send({
                    "type": "websocket.close",
                    "code": 1008,
                    "reason": "User not found",
                })
                return

        # Close old database connections in async context
        close_old_connections()

        # Continue with the WebSocket connection
        return await super().__call__(scope, receive, send)

    async def get_user_by_id(self, user_id):
        # Fetch user by ID asynchronously
        return await User.objects.aget(user_id=user_id)