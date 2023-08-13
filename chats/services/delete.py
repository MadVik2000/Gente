"""
This service contains all the delete services for chats app
"""

from chats.models import ChatSession


def delete_chat_session(chat_session: ChatSession):
    """
    This service is used to soft delete a chat session instance
    """
    assert isinstance(chat_session, ChatSession), "chat_session must be a ChatSession instance"

    chat_session.is_active = False
    chat_session.save()

    return True, "Instance Deleted Successfully"
