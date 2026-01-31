from __future__ import annotations

from typing import Protocol


class SentimentScorer(Protocol):
    async def score(self, text: str) -> float:
        """Return sentiment score normalized to [-1, 1]."""
        raise NotImplementedError
