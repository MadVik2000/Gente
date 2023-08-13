"""
This file contains services to perform CRUD operations on chat session message model
"""

from typing import Union
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from chats.models import ChatSession, ChatSessionMessage

User = get_user_model()


def create_chat_session_message(
    chat_session: Union[ChatSession, str, UUID],
    user: Union[User, str, UUID],
    message: str,
) -> tuple[bool, Union[str, ChatSessionMessage]]:
    """
    This service is used to create a new chat session message instance
    """
    chat_session_message = ChatSessionMessage(
        chat_session_id=chat_session.session_id
        if isinstance(chat_session, ChatSession)
        else chat_session,
        user_id=user.uuid if isinstance(user, User) else user,
        message=message,
    )
    try:
        chat_session_message.save()
    except ValidationError as error:
        return False, error.message

    return True, chat_session_message
