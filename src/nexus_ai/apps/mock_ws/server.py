from __future__ import annotations

import asyncio
import json
import random
from datetime import datetime, timezone

import websockets

from nexus_ai.common.logging import configure_logging, get_logger

log = get_logger({"app": "mock_ws"})

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]


async def handler(ws: websockets.WebSocketServerProtocol) -> None:
    log.info("mock_client_connected")
    prices = {s: random.uniform(50, 50000) for s in SYMBOLS}

    while True:
        await asyncio.sleep(0.05)

        sym = random.choice(SYMBOLS)
        drift = random.uniform(-0.5, 0.5)
        jump = random.random() < 0.002
        if jump:
            drift += random.choice([-1, 1]) * random.uniform(50, 500)

        prices[sym] = max(0.01, prices[sym] + drift)

        msg = {
            "symbol": sym,
            "ts": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
            "price": round(prices[sym], 4),
            "size": round(random.uniform(0.01, 2.0), 4),
            "kind": "trade",
            "source": "mock_ws",
        }
        await ws.send(json.dumps(msg))


async def main() -> None:
    configure_logging("INFO")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        log.info("mock_ws_listening", port=8765)
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
