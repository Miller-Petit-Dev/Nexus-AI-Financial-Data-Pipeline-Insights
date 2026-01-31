from __future__ import annotations

import asyncio
import random
from typing import AsyncIterator

import websockets
from websockets.client import WebSocketClientProtocol

from nexus_ai.common.logging import get_logger


log = get_logger({"component": "ws_client"})


class WebSocketConnector:
    def __init__(self, url: str, ping_interval_s: float, max_backoff_s: float) -> None:
        self._url = url
        self._ping_interval_s = ping_interval_s
        self._max_backoff_s = max_backoff_s

    async def connect_forever(self) -> AsyncIterator[WebSocketClientProtocol]:
        attempt = 0
        while True:
            attempt += 1
            backoff = min(self._max_backoff_s, (2 ** min(attempt, 8)))
            jitter = random.uniform(0.0, 0.25 * backoff)
            delay = backoff + jitter

            try:
                log.info("ws_connect_attempt", url=self._url, attempt=attempt)
                ws = await websockets.connect(
                    self._url,
                    ping_interval=self._ping_interval_s,
                    close_timeout=5,
                    max_queue=1024,
                )
                log.info("ws_connected", url=self._url)
                attempt = 0
                yield ws
            except Exception as e:
                log.warning("ws_connect_failed", url=self._url, err=str(e), retry_s=delay)
                await asyncio.sleep(delay)

    async def recv_lines(self, ws: WebSocketClientProtocol) -> AsyncIterator[str]:
        while True:
            msg = await ws.recv()
            if msg is None:
                return
            if isinstance(msg, bytes):
                msg = msg.decode("utf-8", errors="replace")
            yield msg
