from __future__ import annotations

from typing import Any, Mapping

from redis.asyncio import Redis


class RedisStreams:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def xadd(self, stream: str, fields: Mapping[str, Any], maxlen_approx: int) -> str:
        return await self._redis.xadd(
            name=stream,
            fields={k: str(v) for k, v in fields.items()},
            maxlen=maxlen_approx,
            approximate=True,
        )
