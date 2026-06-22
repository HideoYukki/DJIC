import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Token JWT jest wymagany w query string: ?token=<JWT>
        # Tutaj zakładamy, że middleware już zautentykował użytkownika
        # lub token zostanie zweryfikowany po połączeniu
        self.user_id = self.scope.get('user_id', 'anonymous')
        self.group_name = f'notifications_{self.user_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data'],
        }))
