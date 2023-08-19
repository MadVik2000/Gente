import logging
import time
from datetime import timedelta

from celery import shared_task
from celery.exceptions import Retry
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Prefetch
from django.utils.timezone import now

from chats.models import ChatSession, ChatSessionMessage
from chats.services import create_session_and_session_users
from helpers.caching import CustomRedisCaching

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@shared_task
def remove_expired_users():
    user_queue_cache_key = settings.USER_QUEUE_CACHE_KEY
    redis_client = CustomRedisCaching()
    current_time = int(time.time())

    user_queue_length = redis_client.llen(user_queue_cache_key)
    if not user_queue_length:
        return

    user_queue = redis_client.lrange(key=user_queue_cache_key, instance=False)

    for user in user_queue:
        user_data = redis_client.value_serializer.loads(user)
        if current_time - user_data.get("queue_joining_time") > 30:
            redis_client.lrem(user_queue_cache_key, 0, user)


@shared_task
def add_users_to_session():
    redis_client = CustomRedisCaching()
    total_users_in_queue = redis_client.llen(name=settings.USER_QUEUE_CACHE_KEY)
    if not total_users_in_queue >= 2:
        return

    users = [
        user_data.get("user")
        for user_data in redis_client.lpop(
            name=settings.USER_QUEUE_CACHE_KEY, count=2 * (total_users_in_queue // 2)
        )
    ]
    success, result = create_session_and_session_users(users_list=users)
    if not success:
        logging.error(result)
        raise Retry(result)


@shared_task
def terminate_inactive_sessions():
    inactivation_time = now() - timedelta(minutes=1)
    chat_sessions = ChatSession.objects.filter(
        is_active=True, created_at__lt=inactivation_time
    ).prefetch_related(
        Prefetch(
            "chatsessionmessage_set",
            queryset=ChatSessionMessage.objects.filter(created_at__gte=inactivation_time),
        )
    )

    sessions_to_be_inactivated = []
    for chat_session in chat_sessions:
        if not chat_session.chatsessionmessage_set.exists():
            setattr(chat_session, "is_active", False)
            setattr(chat_session, "session_closed_at", now())
            sessions_to_be_inactivated.append(chat_session)

    if not sessions_to_be_inactivated:
        return

    try:
        ChatSession.objects.bulk_update(
            sessions_to_be_inactivated, fields=["is_active", "session_closed_at"]
        )
    except IntegrityError as error:
        raise Retry(error)
