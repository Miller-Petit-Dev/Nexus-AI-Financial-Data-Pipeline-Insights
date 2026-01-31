from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class NewsItem(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    ts: datetime
    headline: str = Field(min_length=1, max_length=5000)
    source: str = Field(default="news")

    @field_validator("ts")
    @classmethod
    def ensure_tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
