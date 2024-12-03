import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from accounts.models import Notification, ParentProfile
import pytz
from datetime import datetime

class NotificationService:
    @staticmethod
    def add_notification(receiver, description, additional_information=None):
        notification = Notification()
        notification.user_id = receiver  # Assuming user_id is a foreign key
        notification.description = description
        notification.read = False
        notification.save()

        print(str(notification.notification_id))

        # Lấy thời gian UTC và chuyển sang múi giờ mong muốn
        utc_time = notification.created_at
        target_timezone = pytz.timezone("Asia/Ho_Chi_Minh")
        local_time = utc_time.astimezone(target_timezone)

        message = {
            'message': description,
            'time': local_time.strftime('%d/%m/%Y, %H:%M:%S'),  # Hiển thị thời gian theo múi giờ
            'notification_id': str(notification.notification_id),
            'read': False,
            'additional_information': additional_information
        }
        notification.data = message
        notification.save()

        channel_layer = get_channel_layer()
        try:
            async_to_sync(channel_layer.group_send)(
                f'user_{receiver.user_id}',
                {
                    'type': 'notify_user',
                    'notification': message
                }
            )
        except Exception as e:
            # Log the error hoặc xử lý tùy ý
            print(f"Error sending notification to user {receiver}: {e}")