"""
This file contains all the APIs related to chat session messages.
"""

from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from chats.services import create_chat_session_message


class CreateChatSessionMessageAPI(APIView):
    """
    This API is used to create a chat session message.
    """

    permission_classes = (IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        session_id = serializers.UUIDField(required=True)
        message = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        success, chat_session_message = create_chat_session_message(
            chat_session=validated_data["session_id"],
            user=request.user,
            message=validated_data["message"],
        )
        if not success:
            return Response(data=chat_session_message, status=HTTP_400_BAD_REQUEST)

        return Response(status=HTTP_204_NO_CONTENT)
