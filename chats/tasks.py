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
    user_id_hash_cache_key = settings.USER_ID_HASH_CACHE_KEY
    redis_client = CustomRedisCaching()
    current_time = int(time.time())

    user_queue_length = redis_client.llen(user_queue_cache_key)
    if not user_queue_length:
        return

    user_queue = redis_client.lrange(key=user_queue_cache_key, instance=False)
    user_timings = redis_client.hgetall(user_id_hash_cache_key)

    for user in user_queue:
        user_instance = redis_client.value_serializer.loads(user)
        user_time = int(user_timings.get(str(user_instance.uuid), 0))
        if current_time - user_time > 30:
            redis_client.lrem(user_queue_cache_key, 0, user)
            redis_client.hdel(
                user_id_hash_cache_key,
                str(user_instance.uuid),
            )


@shared_task
def add_users_to_session():
    redis_client = CustomRedisCaching()
    total_users_in_queue = redis_client.llen(name=settings.USER_QUEUE_CACHE_KEY)
    if not total_users_in_queue >= 2:
        return

    users = redis_client.lrange(
        key=settings.USER_QUEUE_CACHE_KEY,
        end=(2 * (total_users_in_queue // 2)) - 1,
        instance=False,
    )
    for index, user in enumerate(users):
        redis_client.lrem(
            name=settings.USER_QUEUE_CACHE_KEY,
            value=user,
            count=0,
        )
        users[index] = redis_client.value_serializer.loads(user)

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
