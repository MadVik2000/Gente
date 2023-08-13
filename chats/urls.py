"""
This file contains all the API endpoints for users application.
"""

from django.urls import path

from chats.api import chat_session, chat_session_message

urlpatterns = [
    path("start/", chat_session.StartChatAPI.as_view(), name="start-chat"),
    path(
        "message/", chat_session_message.CreateChatSessionMessageAPI.as_view(), name="send-message"
    ),
    path(
        "sessions/terminate/", chat_session.TerminateSessionAPI.as_view(), name="terminate-session"
    ),
]
