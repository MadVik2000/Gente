"""
This file contains all the creation services related to users application.
"""
from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(name: str, password: str, email: str) -> User:
    """
    This service is used to create a user instance
    """
    user = User.objects.create_user(
        username=name, email=email, password=password
    )
    return user
