from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView
)
from rest_framework.views import APIView
from chat.models import Chat, Contact
from chat.views import get_user_contact
from .serializers import ChatSerializer
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


class ChatListView(ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = (permissions.AllowAny, )

    def get_queryset(self):
        queryset = Chat.objects.all()
        email = self.request.query_params.get('email', None)
        if email is not None:
            contact = get_user_contact(email)
            queryset = contact.chats.all()
        return queryset
    
class ChatView(APIView):

    def get(self, request):
        email = request.query_params.get('email', None)
        contact = get_user_contact(email)
        chat_objs = contact.chats.all()
        serializer_data = ChatSerializer(chat_objs, many=True, context={'request': request})
        return Response(serializer_data.data
            )
        


class ChatDetailView(RetrieveAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.AllowAny, )


class ChatCreateView(CreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated, )


class ChatUpdateView(UpdateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated, )


class ChatDeleteView(DestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated, )



class BroadcastView(APIView):
    pass