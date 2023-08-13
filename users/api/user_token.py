"""
This file contains all the APIs related to user token.
"""
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView


class GenerateUserTokenAPI(APIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    def post(self, request):
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
        return Response(data={"access_token": user.get_user_token}, status=HTTP_200_OK)
