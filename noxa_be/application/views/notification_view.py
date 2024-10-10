import json
import time
from django.http import StreamingHttpResponse
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status

from accounts.models import Notification

"""
API endpoint for SSE notifications. Setup a connection to the server and listen for notifications.

Get all unread notifications for the user and send them to the client before starting to watch for new notifications.

If cache has parent_id already, push all the stacked notifications to user when they connect.
If not, create a new parent_id in cache and wait for notifications to come in.

After sending the notifications, clear the cache for that parent_id.
"""

def sse_notification(request, parent_id):
        def event_stream(): # Call when client connect (call 1 time)
            active_connections = cache.get('active_connections', {})
            cache.set('active_connections', active_connections)

            message = get_unread_notifications(request, parent_id)
            yield f"data: {message}\n\n"

            if parent_id not in active_connections:
                active_connections[parent_id] = []
                cache.set('active_connections', active_connections)

            try:
                while True:
                    active_connections = cache.get('active_connections', {})

                    if parent_id in active_connections and active_connections[parent_id]:
                        notifications = json.dumps(active_connections[parent_id])
                        yield f"data: {notifications}\n\n"
                        print ('send: ', notifications)
                        active_connections[parent_id] = []
                        cache.set('active_connections', active_connections)

                    time.sleep(1)
            except GeneratorExit:
                print ('Client disconnect')
                active_connections.pop(parent_id, None)
                cache.set('active_connections', active_connections)
        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


def get_unread_notifications(request, user_id):
    notifications = Notification.objects.filter(user_id=user_id, read=False).order_by('-created_at')
    
    message = []
    for notification in notifications:
        message.append(json.dumps({
            'message': notification.description,
            'time': notification.created_at.strftime('%d/%m/%Y , %H:%M:%S'),
        }))

    return json.dumps(message)
         