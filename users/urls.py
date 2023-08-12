"""
This file contains all the API endpoints for users application.
"""

from django.urls import path

from users.api import user_token

urlpatterns = [
    path(
        "token/",
        user_token.GenerateUserTokenAPI.as_view(),
        name="generate-user-token",
    ),
]
