"""
This file contains all the API endpoints for users application.
"""

from django.urls import path

from chats.api import create_chat_session_message, start_chat

urlpatterns = [
    path(
        "start/",
        start_chat.StartChatAPI.as_view(),
        name="start-chat",
    ),
    path(
        "message/",
        create_chat_session_message.CreateChatSessionMessageAPI.as_view(),
        name="send-message",
    ),
]
