from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json
import uuid
from .models import BroadcastMessage
#from push_notifications.models import WebPushDevice
from .views import get_last_10_messages, get_group_details, get_user_contact, get_current_chat, broadcast_to_sub_groups

User = get_user_model()


class BroadcastConsumer(WebsocketConsumer):
    pass
    def fetch_messages(self, data):

        messages = get_last_10_messages(self.scope['url_route']['kwargs']['broadcast_id'])
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def fetch_details(self,data):
        messages = get_group_details(self.scope['url_route']['kwargs']['broadcast_id'])
        content = {
            'command': 'details',
            'data': messages
        }
        self.send_message(content)

    def new_message(self, data):
        user_contact = get_user_contact(data['from'])
        message = BroadcastMessage.objects.create(
            user=user_contact,
            combine_id = str(uuid.uuid4()) + "-"+ str(uuid.uuid4()),
            content=data['message'])
        current_chat = get_current_chat(self.scope['url_route']['kwargs']['broadcast_id'])
        broadcast_to_sub_groups(current_chat.id, message)
        # current_chat.messages.add(message)
        # current_chat.save()
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'id': message.id,
            'author': message.user.email,
            'content': message.content,
            'edited': message.edited, 
            'timestamp': str(message.timestamp)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'fetch_details': fetch_details,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['broadcast_id']
        self.room_group_name = 'broadcast_group_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        # await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # await self.accept()

    # def disconnect(self, close_code):
    #     print("AGAGAG")
    #     async_to_sync(self.channel_layer.group_discard)(
    #         self.room_group_name,
    #         self.channel_name
    #     )
    #     # await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

        # await self.channel_layer.group_send(self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': message
        #     })

    def send_message(self, message):
        
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        # device = WebPushDevice.objects.get(registration_id='3', active = True)
        # title = "Message Received"
        # message = "You've got mail"
        # data = json.dumps({"title": title, "message": message})

        # device.send_message(data)
        self.send(text_data=json.dumps(message))
