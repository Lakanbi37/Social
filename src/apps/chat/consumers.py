import json

from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import ChatMessage, Thread

User = get_user_model()


class ChatConsumer(AsyncConsumer):
    def __init__(self, scope):
        super().__init__(scope)
        self.other_username = self.scope['url_route']['kwargs']['username']
        self.thread_obj = await self.get_thread(self.scope['user'], self.other_username)
        self.room_group_name = self.thread_obj.room_group_name  # group

    async def websocket_connect(self, event):
        # self.cfe_chat_thread = thread_obj
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # other_user = await self.get_user(self.other_username)
        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, event):
        message_data = json.loads(event['text'])
        user = self.scope['user']
        username = "unknown"
        if user.is_authenticated:
            username = user.username
        message_data["user"] = username
        final_message_data = json.dumps(message_data)
        if message_data['msg'] == 'Typing...':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_notify',
                    'message': final_message_data
                }
            )
        else:
            c_message = await self.create_chat_message(user, message_data['msg'],
                                                       message_data['msg_type'],
                                                       message_data['media'])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': final_message_data
                }
            )

    async def typing_notify(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['message']
        })

    async def chat_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['message']
        })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def get_thread(self, user, other_username):
        return Thread.objects.get_or_new(user, other_username)[0]

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def create_chat_message(self, user, message, message_type, media):
        return ChatMessage.objects.create(thread=self.thread_obj, user=user, message=message, message_type=message_type, media=media)


class EchoConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print(event)
        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event["text"],
        })
