from __future__ import annotations

from datetime import datetime
from typing import Dict

from redis.asyncio import Redis

from nexus_ai.common.logging import get_logger
from nexus_ai.domain.models.news import NewsItem
from nexus_ai.domain.ports.sentiment import SentimentScorer
from nexus_ai.infrastructure.postgres.repositories import NewsRepository

log = get_logger({"component": "news_processor"})


def _news_from_stream(fields: Dict[str, str]) -> NewsItem:
    return NewsItem.model_validate(
        {
            "symbol": fields["symbol"],
            "ts": datetime.fromisoformat(fields["ts"]),
            "headline": fields["headline"],
            "source": fields.get("source", "news"),
        }
    )


class NewsProcessor:
    def __init__(
        self,
        redis: Redis,
        repo: NewsRepository,
        scorer: SentimentScorer,
        group: str,
        consumer: str,
        in_stream: str,
    ) -> None:
        self._redis = redis
        self._repo = repo
        self._scorer = scorer
        self._group = group
        self._consumer = consumer
        self._in = in_stream

    async def ensure_group(self) -> None:
        try:
            await self._redis.xgroup_create(self._in, self._group, id="0-0", mkstream=True)
        except Exception:
            pass

    async def run_forever(self) -> None:
        await self.ensure_group()
        log.info("news_processor_started", stream=self._in, group=self._group, consumer=self._consumer)

        while True:
            resp = await self._redis.xreadgroup(
                groupname=self._group,
                consumername=self._consumer,
                streams={self._in: ">"},
                count=64,
                block=2000,
            )
            if not resp:
                continue

            for (_, messages) in resp:
                for msg_id, fields in messages:
                    await self._handle_one(msg_id, fields)

    async def _handle_one(self, msg_id: str, fields: Dict[str, str]) -> None:
        try:
            item = _news_from_stream(fields)
            sentiment = await self._scorer.score(item.headline)
            await self._repo.insert_scored(item, sentiment)
            await self._redis.xack(self._in, self._group, msg_id)
        except Exception as e:
            log.warning("news_process_failed", id=msg_id, err=str(e))
