"""
This file contains all the APIs related to user token.
"""
from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from users.helpers import generate_token


class GenerateUserToken(APIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    def get(self, request):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)
        user_details = serializer.validated_data

        user = authenticate(
            email=user_details.get("email"),
            password=user_details.get("password"),
        )
        if not user:
            return Response(
                data={"errors": "Invalid Credentials"},
                status=HTTP_400_BAD_REQUEST,
            )

        token = cache.get(f"{user.email}_access_token")
        if not token:
            token = generate_token(user=user)
            cache.set(
                f"{user.email}_access_token", token, timeout=60 * 60 * 24 * 3
            )
        return Response(data={"access_token": token}, status=HTTP_200_OK)
