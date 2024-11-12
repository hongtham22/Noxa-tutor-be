import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from accounts.models import JobPost, Notification
from accounts.enums import Role, Status

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            user = self.scope["user"]

            if user.is_anonymous:
                await self.accept()
                await self.send(text_data=json.dumps({"type": "error", "message": "Please enter a valid user ID"}))
                await self.close()
                return

            await self.channel_layer.group_add(
                f"user_{user.user_id}",
                self.channel_name
            )
            await self.accept()

            unread_notifications = await self.get_unread_notifications(user)
            if unread_notifications:
                await self.send(text_data=json.dumps({"type": "unread notifications", "notifications": unread_notifications}))

            if (user.role == Role.ADMIN):
                unhandled_posts = await self.get_unhandled_posts()
                if unhandled_posts:
                    await self.send(text_data=json.dumps({"type": "unhandled posts", "posts": unhandled_posts}))
                        
        except Exception as e:
            
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    async def disconnect(self, close_code):
        try:
            user = self.scope["user"]
            await self.channel_layer.group_discard(
                f"user_{user.user_id}",
                self.channel_name
            )
        except Exception as e:
            #print (str(e))
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            user = self.scope["user"]

            if data["action"] == "mark_as_read":
                notification_ids = data["notification_ids"]
                await self.mark_notifications_as_read(user, notification_ids)
        except Exception as e:
            print ('bla bla bal'+str(e))
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    async def get_unhandled_posts(self):
        try:
            unhandled_posts = await sync_to_async(JobPost.objects.filter)(status=Status.PENDING_APPROVAL)
            unhandled_posts_list = []
            for post in await sync_to_async(list)(unhandled_posts):
                unhandled_posts_list.append(
                    {"id": str(post.post_id), "content": post.description, "created_at": str(post.created_at)}
                )
            return unhandled_posts_list
        except Exception as e:
            print (str(e))
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    async def notify_user(self, event):
        try:
            notification = event["notification"]
            await self.send(text_data=json.dumps({"type": "new_notification", "notification": notification}))
        except Exception as e:
            print ('notify' + str(e))
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    async def get_unread_notifications(self, user):
        try:
            unread_notifications = await sync_to_async(Notification.objects.filter)(user_id=user, read=False)
            
            unread_notifications_list = []
            for n in await sync_to_async(list)(unread_notifications):
                unread_notifications_list.append(
                    {"id": str(n.notification_id), "content": n.description, "created_at": str(n.created_at), "is_read": n.read}
                )
            return unread_notifications_list
        except Exception as e:
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))
            return []

    async def mark_notifications_as_read(self, user, notification_ids):
        try:
            await sync_to_async(Notification.objects.filter(user_id=user, notification_id__in=notification_ids).update)(read=True)
        except Exception as e:
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))