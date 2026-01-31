from __future__ import annotations

import asyncio

from nexus_ai.common.logging import configure_logging, get_logger
from nexus_ai.config.settings import Settings
from nexus_ai.infrastructure.redis.client import create_redis
from nexus_ai.infrastructure.redis.streams import RedisStreams
from nexus_ai.infrastructure.postgres.pool import create_pool
from nexus_ai.infrastructure.postgres.repositories import TickRepository, NewsRepository
from nexus_ai.infrastructure.anomaly.adaptive_zscore import AdaptiveZScore
from nexus_ai.application.processing.tick_processor import TickProcessor
from nexus_ai.application.processing.news_processor import NewsProcessor
from nexus_ai.infrastructure.nlp.finbert import FinBERTConfig, FinBERTSentiment

log = get_logger({"app": "processor"})


async def run() -> None:
    settings = Settings()
    configure_logging(settings.log_level)

    redis = create_redis(settings.redis_url)
    streams = RedisStreams(redis)

    pool = await create_pool(settings.pg_dsn)
    tick_repo = TickRepository(pool)
    news_repo = NewsRepository(pool)

    z = AdaptiveZScore(window=settings.anomaly_z_window, threshold=settings.anomaly_z_threshold)

    ticks = TickProcessor(
        redis=redis,
        streams=streams,
        repo=tick_repo,
        group=settings.ticks_group,
        consumer=settings.ticks_consumer,
        in_stream=settings.redis_stream_ticks,
        out_stream="clean:ticks",
        maxlen_approx=settings.redis_maxlen_approx,
        z=z,
    )

    finbert = FinBERTSentiment(FinBERTConfig(model_id=settings.finbert_model_id))
    news = NewsProcessor(
        redis=redis,
        repo=news_repo,
        scorer=finbert,
        group=settings.news_group,
        consumer=settings.news_consumer,
        in_stream=settings.redis_stream_news,
    )

    await asyncio.gather(
        ticks.run_forever(),
        news.run_forever(),
    )


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
