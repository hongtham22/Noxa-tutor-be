# posts/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class JobPostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

    async def send_status_change(self, event):
        await self.send(text_data=json.dumps({
            # 'post_id': event['post_id'],
            'status': event['status'],
        }))