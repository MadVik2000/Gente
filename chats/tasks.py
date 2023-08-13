import time

from celery import shared_task
from django.conf import settings

from helpers.caching import CustomRedisCaching


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
            redis_client.hdel(user_id_hash_cache_key, str(user_instance.uuid))
