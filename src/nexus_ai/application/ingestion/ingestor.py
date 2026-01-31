from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

from nexus_ai.common.logging import get_logger
from nexus_ai.domain.models.market_data import Tick
from nexus_ai.infrastructure.redis.streams import RedisStreams

log = get_logger({"component": "ingestor"})


def _normalize_tick(payload: Dict[str, Any]) -> Dict[str, Any]:
    ts_raw = payload.get("ts")
    if isinstance(ts_raw, str):
        ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
    elif isinstance(ts_raw, (int, float)):
        ts = datetime.fromtimestamp(float(ts_raw), tz=timezone.utc)
    else:
        ts = datetime.now(tz=timezone.utc)

    return {
        "symbol": str(payload.get("symbol", "")).upper(),
        "ts": ts,
        "price": float(payload.get("price", 0.0)),
        "size": float(payload.get("size", 1.0)),
        "source": str(payload.get("source", "ws")),
        "kind": payload.get("kind", "trade"),
    }


class TickIngestor:
    def __init__(self, streams: RedisStreams, stream_name: str, maxlen_approx: int) -> None:
        self._streams = streams
        self._stream = stream_name
        self._maxlen = maxlen_approx

    async def handle_message(self, raw: str) -> None:
        try:
            payload = json.loads(raw)
        except Exception:
            log.warning("ingest_invalid_json", raw_preview=raw[:200])
            return

        try:
            normalized = _normalize_tick(payload)
            tick = Tick.model_validate(normalized)
        except Exception as e:
            log.warning("ingest_validation_failed", err=str(e), payload=payload)
            return

        fields = {
            "symbol": tick.symbol,
            "ts": tick.ts.isoformat(),
            "price": tick.price,
            "size": tick.size,
            "source": tick.source,
            "kind": tick.kind,
        }
        msg_id = await self._streams.xadd(self._stream, fields, self._maxlen)
        log.debug("ingest_published", stream=self._stream, id=msg_id, symbol=tick.symbol)
