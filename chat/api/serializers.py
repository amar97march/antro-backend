from rest_framework import serializers

from chat.models import Chat, Contact
from chat.views import get_user_contact


class ContactSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class ChatSerializer(serializers.ModelSerializer):
    participants = ContactSerializer(many=True)

    class Meta:
        model = Chat
        fields = ('id', 'messages', 'participants')
        read_only = ('id')

    def create(self, validated_data):
        print(validated_data)
        participants = validated_data.pop('participants')
        chat = Chat()
        chat.save()
        for email in participants:
            contact = get_user_contact(email)
            chat.participants.add(contact)
        chat.save()
        return chat
    
    def to_representation(self, data):
        data = super(ChatSerializer, self).to_representation(data)
        print(data, "ADATAT")
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        receiver = None
        for participant in data['participants']:
            if (user != user.email):
                receiver = participant
        data['receiver'] = receiver
        return data
    


# do in python shell to see how to serialize data

# from chat.models import Chat
# from chat.api.serializers import ChatSerializer
# chat = Chat.objects.get(id=1)
# s = ChatSerializer(instance=chat)
# s
# s.data
