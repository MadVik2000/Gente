"""
This service contains all the delete services for chats app
"""

from django.contrib.auth import get_user_model

from chats.models import ChatSession

User = get_user_model()


def delete_chat_session(chat_session: ChatSession, deleted_by: User):
    """
    This service is used to soft delete a chat session instance
    """
    assert isinstance(chat_session, ChatSession), "chat_session must be a ChatSession instance"

    chat_session.is_active = False
    chat_session.deleted_by = deleted_by
    chat_session.save()

    return True, "Instance Deleted Successfully"
