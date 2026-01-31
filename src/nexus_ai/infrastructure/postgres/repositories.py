from __future__ import annotations

from typing import Optional

import asyncpg

from nexus_ai.domain.models.market_data import Tick
from nexus_ai.domain.models.news import NewsItem


class TickRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def insert_clean(self, tick: Tick, zscore: Optional[float], is_anomaly: bool) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ticks_clean(symbol, ts, price, size, source, kind, zscore, is_anomaly)
                VALUES($1,$2,$3,$4,$5,$6,$7,$8)
                """,
                tick.symbol,
                tick.ts,
                float(tick.price),
                float(tick.size),
                tick.source,
                tick.kind,
                float(zscore) if zscore is not None else None,
                bool(is_anomaly),
            )


class NewsRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def insert_scored(self, item: NewsItem, sentiment: float) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO news_sentiment(symbol, ts, headline, source, sentiment)
                VALUES($1,$2,$3,$4,$5)
                """,
                item.symbol,
                item.ts,
                item.headline,
                item.source,
                float(sentiment),
            )
