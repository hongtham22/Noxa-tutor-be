import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from accounts.models import Notification

class NotificationService:
    @staticmethod
    def add_notification(receiver, description):
        notification = Notification()
        notification.user_id = receiver  # Assuming user_id is a foreign key
        notification.description = description
        notification.read = False
        notification.save()

        message = json.dumps({
            'message': description,
            'time': notification.created_at.strftime('%d/%m/%Y , %H:%M:%S'),
            'notification_id': str(notification.notification_id),
            'read': False
        })

        channel_layer = get_channel_layer()
        try:
            async_to_sync(channel_layer.group_send)(
                f'user_{receiver}',
                {
                    'type': 'notify_user',
                    'message': message
                }
            )
        except Exception as e:
            # Log the error or handle it as needed
            print(f"Error sending notification to user {receiver}: {e}")