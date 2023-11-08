from django.urls import re_path

from .consumers import ChatConsumer
from organisation.consumers import BroadcastConsumer

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>[^/]+)/$', ChatConsumer.as_asgi()),
    re_path(r'^ws/broadcast/(?P<broadcast_id>[^/]+)/$', BroadcastConsumer.as_asgi()),
]
