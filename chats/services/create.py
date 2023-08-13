"""
This file contains all create services for chats module
"""

from typing import Union
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from chats.helpers import get_user_pairs
from chats.models import ChatSession, ChatSessionMessage, ChatSessionUser

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


User = get_user_model()


def create_session_and_session_users(
    users_list: list[User],
) -> tuple[bool, Union[str, tuple[ChatSession, ChatSessionUser]]]:
    """
    This service is used bulk create chat sessions and chat session users.
    """

    users_pairs = get_user_pairs(users_list)

    chat_sessions = []
    chat_session_users = []
    try:
        for users in users_pairs:
            chat_session = ChatSession()
            chat_session.clean()
            chat_session.clean_fields()
            chat_sessions.append(chat_session)

            for user in users:
                chat_session_user = ChatSessionUser(chat_session=chat_session, user=user)
                chat_session_user.clean()
                chat_session_users.append(chat_session_user)

        chat_sessions = ChatSession.objects.bulk_create(chat_sessions)
        chat_session_users = ChatSessionUser.objects.bulk_create(chat_session_users)

    except (ValidationError, IntegrityError) as error:
        return False, error

    return True, (chat_sessions, chat_session_users)
