from __future__ import annotations

from collections import deque
from math import sqrt
from typing import Deque, Optional


class AdaptiveZScore:
    def __init__(self, window: int, threshold: float) -> None:
        self._w = window
        self._t = threshold
        self._buf: Deque[float] = deque(maxlen=window)
        self._sum = 0.0
        self._sumsq = 0.0

    def update(self, x: float) -> None:
        if len(self._buf) == self._buf.maxlen:
            old = self._buf[0]
            self._sum -= old
            self._sumsq -= old * old

        self._buf.append(x)
        self._sum += x
        self._sumsq += x * x

    def score(self, x: float) -> Optional[float]:
        n = len(self._buf)
        if n < max(10, self._w // 6):
            return None
        mean = self._sum / n
        var = (self._sumsq / n) - (mean * mean)
        if var <= 1e-12:
            return 0.0
        std = sqrt(var)
        return (x - mean) / std

    def is_anomaly(self, x: float) -> bool:
        z = self.score(x)
        if z is None:
            return False
        return abs(z) >= self._t
