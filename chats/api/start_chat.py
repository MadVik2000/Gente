"""
This file contains all the APIs related to starting a chat.
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from chats.helpers import send_user_to_queue
from chats.models import ChatSession


class StartChatAPI(APIView):
    """
    This API is used to put user into a chat queue.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if ChatSession.objects.filter(
            user=request.user, chat_session__is_active=True
        ).exists():
            return Response(
                status=HTTP_400_BAD_REQUEST,
                data={
                    "errors": "User already present in an active chat session."
                },
            )
        if not send_user_to_queue(user=request.user):
            return Response(
                status=HTTP_400_BAD_REQUEST,
                data={"errors": "User already present in search queue."},
            )
        return Response(status=HTTP_204_NO_CONTENT)
