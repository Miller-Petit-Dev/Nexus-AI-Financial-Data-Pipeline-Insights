from __future__ import annotations

import asyncio

from nexus_ai.common.logging import configure_logging, get_logger
from nexus_ai.config.settings import Settings
from nexus_ai.application.ingestion.websocket_client import WebSocketConnector
from nexus_ai.application.ingestion.ingestor import TickIngestor
from nexus_ai.infrastructure.redis.client import create_redis
from nexus_ai.infrastructure.redis.streams import RedisStreams

log = get_logger({"app": "ingestor"})


async def run() -> None:
    settings = Settings()
    configure_logging(settings.log_level)

    redis = create_redis(settings.redis_url)
    streams = RedisStreams(redis)

    ingestor = TickIngestor(
        streams=streams,
        stream_name=settings.redis_stream_ticks,
        maxlen_approx=settings.redis_maxlen_approx,
    )

    ws = WebSocketConnector(
        url=settings.ws_url,
        ping_interval_s=settings.ws_ping_interval_s,
        max_backoff_s=settings.ws_max_backoff_s,
    )

    async for conn in ws.connect_forever():
        try:
            async for msg in ws.recv_lines(conn):
                await ingestor.handle_message(msg)
        except Exception as e:
            log.warning("ws_session_failed", err=str(e))
        finally:
            try:
                await conn.close()
            except Exception:
                pass


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
