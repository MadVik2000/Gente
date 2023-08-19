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

    user_queues = redis_client.hgetall(user_queue_cache_key)
    for queue, users_queue in user_queues.items():
        if not users_queue:
            continue

        new_users_queue = []

        for user_data in users_queue:
            if current_time - user_data.get("queue_joining_time") > 60:
                continue
            new_users_queue.append(user_data)
        if not sorted(users_queue, key=lambda element: sorted(element.items())) == sorted(
            new_users_queue, key=lambda element: sorted(element.items())
        ):
            redis_client.hset(name=user_queue_cache_key, key=queue, value=new_users_queue)


@shared_task
def add_users_to_session():
    user_queue_cache_key = settings.USER_QUEUE_CACHE_KEY
    redis_client = CustomRedisCaching()

    user_queues = redis_client.hgetall(user_queue_cache_key)
    for queue, user_queue in user_queues.items():
        queue_length = len(user_queue)
        if not queue_length >= 2:
            continue

        session_users = user_queue[: 2 * (queue_length // 2)]
        remaining_users = user_queue[2 * (queue_length // 2) :]

        success, result = create_session_and_session_users(
            users_list=[user_data.get("user") for user_data in session_users]
        )
        if not success:
            logging.error(result)
            raise Retry(result)

        redis_client.hset(name=user_queue_cache_key, key=queue, value=remaining_users)


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
