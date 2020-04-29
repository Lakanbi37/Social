from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from apps.chat.consumers import ChatConsumer

application = ProtocolTypeRouter({
    # Websocket chat handler
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    # url(r"chat/", ChatConsumer, name='chat')
                    path(r"messages/<slug:username>/",
                         ChatConsumer, name='chat')
                ]
            )
        ),
    ),
})
