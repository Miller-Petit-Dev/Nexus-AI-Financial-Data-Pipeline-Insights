from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, PositiveFloat, field_validator


class Tick(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    ts: datetime
    price: PositiveFloat
    size: PositiveFloat = Field(default=1.0)
    source: str = Field(default="ws")
    kind: Literal["trade", "quote"] = "trade"

    @field_validator("ts")
    @classmethod
    def ensure_tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
