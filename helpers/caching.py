"""
This file contains custom caching modules used throughout the project
"""

from collections.abc import Iterable
from typing import Union

from django.core.cache.backends.redis import RedisSerializer
from redis.client import Redis


class CustomRedisCaching(Redis):
    def __init_(self, *args) -> None:
        return super().__init__(*args)
        self.value_serializer = RedisSerializer()

    value_serializer = RedisSerializer()

    def lpush(self, key: str, values: Iterable) -> int:
        """
        Customised redis LPUSH command to store django model instances
        """
        values = [self.value_serializer.dumps(value) for value in values]
        return super().lpush(key, *values)

    def lrange(
        self, key: str, start: int = 0, end: int = -1, instance: bool = True
    ) -> list:
        """
        Customised redis LRANGE command to retrieve django model instances
        """
        values = list(super().lrange(name=key, start=start, end=end))
        return (
            [self.value_serializer.loads(value) for value in values]
            if instance
            else values
        )

    def rpush(self, key: str, values: Iterable) -> int:
        """
        Customised redis LPUSH command to store django model instances
        """
        values = [self.value_serializer.dumps(value) for value in values]
        return super().rpush(key, *values)

    def lpop(self, name, count: Union[int, None] = None) -> list:
        values = list(super().lpop(name, count))
        if values:
            return (
                [self.value_serializer.loads(value) for value in values]
                if isinstance(values, list)
                else [self.value_serializer.loads(values)]
            )
        else:
            return []

    def hgetall(self, name: str) -> dict:
        return {
            field.decode("utf-8"): value.decode("utf-8")
            for field, value in super().hgetall(name).items()
        }
