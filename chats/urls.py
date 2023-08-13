"""
This file contains all the API endpoints for users application.
"""

from django.urls import path

from chats.api import start_chat

urlpatterns = [
    path(
        "start/",
        start_chat.StartChatAPI.as_view(),
        name="start-chat",
    ),
]
