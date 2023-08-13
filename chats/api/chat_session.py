"""
This file contains all the APIs related to starting a chat.
"""
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from chats.helpers import send_user_to_queue
from chats.models import ChatSessionUser
from chats.services import delete_chat_session


class StartChatAPI(APIView):
    """
    This API is used to put user into a chat queue.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if ChatSessionUser.objects.filter(user=request.user, chat_session__is_active=True).exists():
            return Response(
                status=HTTP_400_BAD_REQUEST,
                data={"errors": "User already present in an active chat session."},
            )
        if not send_user_to_queue(user=request.user):
            return Response(
                status=HTTP_400_BAD_REQUEST,
                data={"errors": "User already present in search queue."},
            )
        return Response(status=HTTP_204_NO_CONTENT)


class TerminateSessionAPI(APIView):
    """
    This API is used to terminate a chat session.
    """

    permission_classes = (IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        session_id = serializers.UUIDField(required=True)

    def get_queryset(self, request, session_id):
        return ChatSessionUser.objects.filter(
            user=request.user, chat_session_id=session_id, chat_session__is_active=True
        ).select_related("chat_session")

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        try:
            chat_session_user = self.get_queryset(
                request=request, session_id=validated_data["session_id"]
            ).get()
        except ChatSessionUser.DoesNotExist:
            return Response(
                data={"errors": "No active sessions found for user with given session id"},
                status=HTTP_400_BAD_REQUEST,
            )

        success, response = delete_chat_session(
            chat_session=chat_session_user.chat_session, terminated_by=request.user
        )
        if not success:
            return Response(data={"errors": response}, status=HTTP_400_BAD_REQUEST)

        return Response(status=HTTP_204_NO_CONTENT)
