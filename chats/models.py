from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from helpers.models import CustomModel

User = get_user_model()


class ChatSession(CustomModel):
    """
    This model stores all the chat sessions
    """

    session_id = models.UUIDField(default=uuid4, unique=True, db_index=True)
    session_closed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def validate_session_closed_at(self):
        if (
            self.pk
            and self.session_closed_at
            and (
                self.created_at >= self.session_closed_at
                or self.updated_at > self.session_closed_at
            )
        ):
            raise ValidationError(
                "Session Closing time cannot be greater than session start time or session updation time"
            )

    def validate_is_active(self):
        if self.pk and self.is_active and self.diff.get("is_active"):
            raise ValidationError(
                "Chat Session cannot be activated again once inactivated"
            )

    def __str__(self):
        return str(self.session_id)

    def clean(self):
        super().clean()
        self.validate_session_closed_at()
        self.validate_is_active()


class ChatSessionUser(CustomModel):
    """
    This models stores all the chat session users
    """

    chat_session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, to_field="session_id"
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def validate_instance_creation(self):
        if not self.chat_session.is_active:
            raise ValidationError(
                "Chat Session User cannot be created for inactive chat session"
            )

    def validate_chat_session_users(self):
        if ChatSessionUser.objects.filter(
            chat_session__is_active=True, user=self.user
        ).exists():
            raise ValidationError(
                "User already exists in an active chat session"
            )

        if (
            not self.pk
            and ChatSessionUser.objects.filter(
                chat_session_id=self.chat_session_id
            ).count()
            == 2
        ):
            raise ValidationError(
                "Chat Session cannot have more than two users at a time."
            )

        if self.pk and self.diff.get("user"):
            raise ValidationError("User cannot be changed in a chat session")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("chat_session", "user"),
                name="chat_session_user_unique_constraint",
            )
        ]

    def __str__(self):
        return str(self.user)

    def clean(self):
        super().clean()
        self.validate_instance_creation()

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        self.validate_chat_session_users()


class ChatSessionMessage(CustomModel):
    """
    This model stores all the chat session messages
    """

    chat_session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, to_field="session_id"
    )
    message = models.TextField()
    sequence = models.BigIntegerField(editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        help_text="User from which message was originated",
    )

    def validate_instance_creation(self):
        if not self.chat_session.is_active:
            raise ValidationError(
                "Chat Session Message cannot be added for inactive chat session"
            )

    def validate_chat_session_user(self):
        if not ChatSessionUser.objects.filter(
            chat_session_id=self.chat_session_id, user_id=self.user_id
        ).exists():
            raise ValidationError(
                "Chat message cannot be initiated from a user who is not part of that chat session"
            )

        if self.pk and self.diff.get("user"):
            raise ValidationError("Chat Session Message user cannot be updated")

    def validate_message(self):
        if self.pk and self.diff.get("message"):
            raise ValidationError("Chat Session Message cannot be updated")

    def validate_sequence(self):
        if self.pk and self.diff.get("sequence"):
            raise ValidationError(
                "Chat Session Message Sequence cannot be updated"
            )

        if not self.pk and not self.sequence:
            last_sequence = (
                ChatSessionMessage.objects.filter(
                    chat_session_id=self.chat_session_id
                )
                .order_by("-sequence")
                .first()
            )
            if not last_sequence:
                self.sequence = 1
            else:
                self.sequence = last_sequence.sequence + 1

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("chat_session", "sequence"),
                name="chat_session_sequence_unique_key",
            )
        ]

    def __str__(self):
        return f"{str(self.chat_session)}_{str(self.user)}"

    def clean(self):
        super().clean()
        self.validate_instance_creation()
        self.validate_message()

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        self.validate_chat_session_user()
        self.validate_sequence()
