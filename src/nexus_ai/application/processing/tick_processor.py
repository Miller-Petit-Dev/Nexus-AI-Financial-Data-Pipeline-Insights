from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from redis.asyncio import Redis

from nexus_ai.common.logging import get_logger
from nexus_ai.domain.models.market_data import Tick
from nexus_ai.domain.ports.anomaly import AnomalyDetector
from nexus_ai.infrastructure.postgres.repositories import TickRepository
from nexus_ai.infrastructure.redis.streams import RedisStreams

log = get_logger({"component": "tick_processor"})


def _tick_from_stream(fields: Dict[str, str]) -> Tick:
    return Tick.model_validate(
        {
            "symbol": fields["symbol"],
            "ts": datetime.fromisoformat(fields["ts"]),
            "price": float(fields["price"]),
            "size": float(fields.get("size", "1.0")),
            "source": fields.get("source", "ws"),
            "kind": fields.get("kind", "trade"),
        }
    )


class TickProcessor:
    def __init__(
        self,
        redis: Redis,
        streams: RedisStreams,
        repo: TickRepository,
        group: str,
        consumer: str,
        in_stream: str,
        out_stream: str,
        maxlen_approx: int,
        z: AnomalyDetector,
    ) -> None:
        self._redis = redis
        self._streams = streams
        self._repo = repo
        self._group = group
        self._consumer = consumer
        self._in = in_stream
        self._out = out_stream
        self._maxlen = maxlen_approx
        self._z = z

    async def ensure_group(self) -> None:
        try:
            await self._redis.xgroup_create(self._in, self._group, id="0-0", mkstream=True)
        except Exception:
            pass

    async def run_forever(self) -> None:
        await self.ensure_group()
        log.info("ticks_processor_started", stream=self._in, group=self._group, consumer=self._consumer)

        while True:
            resp = await self._redis.xreadgroup(
                groupname=self._group,
                consumername=self._consumer,
                streams={self._in: ">"},
                count=512,
                block=2000,
            )
            if not resp:
                continue

            for (_, messages) in resp:
                for msg_id, fields in messages:
                    await self._handle_one(msg_id, fields)

    async def _handle_one(self, msg_id: str, fields: Dict[str, str]) -> None:
        try:
            tick = _tick_from_stream(fields)

            zscore: Optional[float] = self._z.score(float(tick.price))
            is_anom = self._z.is_anomaly(float(tick.price))
            self._z.update(float(tick.price))

            await self._repo.insert_clean(tick, zscore, is_anom)

            out_fields: Dict[str, Any] = {
                "symbol": tick.symbol,
                "ts": tick.ts.isoformat(),
                "price": tick.price,
                "size": tick.size,
                "source": tick.source,
                "kind": tick.kind,
                "zscore": zscore if zscore is not None else "",
                "is_anomaly": int(is_anom),
            }
            await self._streams.xadd(self._out, out_fields, self._maxlen)

            await self._redis.xack(self._in, self._group, msg_id)
        except Exception as e:
            log.warning("ticks_process_failed", id=msg_id, err=str(e))
