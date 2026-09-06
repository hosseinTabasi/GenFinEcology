"""Bootstrap confidence intervals over events (or cells).

Reports mean and 95% percentile CI from actual resamples — never invented.
"""
from __future__ import annotations

import hashlib
import random
from typing import Any, Callable


def _rng(seed: int, tag: str) -> random.Random:
    h = hashlib.sha256(f"boot:{seed}:{tag}".encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def percentile_ci(samples: list[float], alpha: float = 0.05) -> dict[str, float]:
    if not samples:
        return {"mean": 0.0, "ci_low": 0.0, "ci_high": 0.0, "B": 0}
    xs = sorted(samples)
    B = len(xs)
    mean = sum(xs) / B
    lo_i = int((alpha / 2) * (B - 1))
    hi_i = int((1 - alpha / 2) * (B - 1))
    return {
        "mean": round(mean, 6),
        "ci_low": round(xs[lo_i], 6),
        "ci_high": round(xs[hi_i], 6),
        "B": B,
    }


def bootstrap_over_events(
    event_ids: list[str],
    statistic_fn: Callable[[list[str]], float],
    B: int = 200,
    seed: int = 20260311,
    tag: str = "default",
) -> dict[str, float]:
    """Resample events with replacement; compute statistic each time."""
    if not event_ids:
        return percentile_ci([])
    rng = _rng(seed, tag)
    samples: list[float] = []
    n = len(event_ids)
    for b in range(B):
        draw = [event_ids[rng.randrange(n)] for _ in range(n)]
        samples.append(float(statistic_fn(draw)))
    return percentile_ci(samples)
