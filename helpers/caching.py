"""
This file contains custom caching modules used throughout the project
"""

from collections.abc import Iterable
from typing import Any, Optional, Union

from django.core.cache.backends.redis import RedisSerializer
from redis.client import Redis
from redis.exceptions import DataError


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
        self, key: str, start: int = 0, end: int = -1, instance: Optional[bool] = True
    ) -> list:
        """
        Customised redis LRANGE command to retrieve django model instances
        """
        values = list(super().lrange(name=key, start=start, end=end))
        return [self.value_serializer.loads(value) for value in values] if instance else values

    def rpush(self, key: str, values: Iterable) -> int:
        """
        Customised redis LPUSH command to store django model instances
        """
        values = [self.value_serializer.dumps(value) for value in values]
        return super().rpush(key, *values)

    def lpop(self, name: str, count: Union[int, None] = None) -> list:
        values = list(super().lpop(name, count))
        if values:
            return (
                [self.value_serializer.loads(value) for value in values]
                if isinstance(values, list)
                else [self.value_serializer.loads(values)]
            )
        else:
            return []

    def hset(
        self,
        name: str,
        key: Optional[str] = None,
        value: Optional[Any] = None,
        mapping: Optional[dict[str, Any]] = None,
        items: Optional[list[Any]] = [],
    ) -> int:
        if key:
            if value is None:
                raise DataError("'hset' with given key but no value to it")
            items.extend([key, self.value_serializer.dumps(value)])

        if mapping:
            for mapping_key, mapping_value in mapping.items():
                items.extend([mapping_key, self.value_serializer.dumps(mapping_value)])

        return super().hset(name=name, items=items)

    def hget(self, name: str, key: str) -> Any:
        value = super().hget(name, key)
        return self.value_serializer.loads(value) if value else None

    def hgetall(self, name: str) -> dict:
        return {
            field.decode("utf-8"): self.value_serializer.loads(value)
            for field, value in super().hgetall(name).items()
        }
