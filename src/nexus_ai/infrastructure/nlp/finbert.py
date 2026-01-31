from __future__ import annotations

import asyncio
from dataclasses import dataclass

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

from nexus_ai.domain.ports.sentiment import SentimentScorer


@dataclass(frozen=True)
class FinBERTConfig:
    model_id: str


class FinBERTSentiment(SentimentScorer):
    def __init__(self, cfg: FinBERTConfig) -> None:
        self._tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
        self._model = AutoModelForSequenceClassification.from_pretrained(cfg.model_id)
        self._model.eval()

    def _infer(self, text: str) -> float:
        inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            logits = self._model(**inputs).logits[0]
        probs = torch.softmax(logits, dim=0)
        p_neg = float(probs[0])
        p_pos = float(probs[2])
        return max(-1.0, min(1.0, p_pos - p_neg))

    async def score(self, text: str) -> float:
        return await asyncio.to_thread(self._infer, text)
