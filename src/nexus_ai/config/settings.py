from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    ws_url: str = Field(default="ws://mock-ws:8765", alias="WS_URL")
    ws_ping_interval_s: float = Field(default=15.0, alias="WS_PING_INTERVAL_S")
    ws_max_backoff_s: float = Field(default=30.0, alias="WS_MAX_BACKOFF_S")

    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    redis_stream_ticks: str = Field(default="raw:ticks", alias="REDIS_STREAM_TICKS")
    redis_stream_news: str = Field(default="raw:news", alias="REDIS_STREAM_NEWS")
    redis_maxlen_approx: int = Field(default=200_000, alias="REDIS_STREAM_MAXLEN")

    pg_dsn: str = Field(
        default="postgresql://postgres:postgres@postgres:5432/nexus",
        alias="PG_DSN",
    )

    ticks_group: str = Field(default="ticks-group", alias="TICKS_GROUP")
    ticks_consumer: str = Field(default="ticks-consumer-1", alias="TICKS_CONSUMER")

    news_group: str = Field(default="news-group", alias="NEWS_GROUP")
    news_consumer: str = Field(default="news-consumer-1", alias="NEWS_CONSUMER")

    anomaly_z_window: int = Field(default=60, alias="ANOMALY_Z_WINDOW")
    anomaly_z_threshold: float = Field(default=4.0, alias="ANOMALY_Z_THRESHOLD")

    finbert_model_id: str = Field(default="ProsusAI/finbert", alias="FINBERT_MODEL_ID")
