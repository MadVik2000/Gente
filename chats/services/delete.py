"""
This service contains all the delete services for chats app
"""

from typing import Optional

from django.contrib.auth import get_user_model
from django.utils.timezone import now

from chats.models import ChatSession

User = get_user_model()


def delete_chat_session(
    chat_session: ChatSession,
    deleted_by: Optional[User] = None,
    terminated_by: Optional[User] = None,
):
    """
    This service is used to soft delete a chat session instance
    """
    assert isinstance(chat_session, ChatSession), "chat_session must be a ChatSession instance"

    setattr(chat_session, "is_active", False)
    setattr(chat_session, "deleted_by", deleted_by)
    setattr(chat_session, "session_terminated_by", terminated_by)
    setattr(chat_session, "session_closed_at", now())

    chat_session.save()

    return True, "Instance Deleted Successfully"
