"""Layer C / C+ — contamination bias, multi-round ecology, amplification, tails."""
from __future__ import annotations

import hashlib
import random
from typing import Any, Iterable


def _sentiment_of_text(text: str, bull_terms: set[str], bear_terms: set[str]) -> float:
    toks = text.lower().split()
    bull = sum(1 for t in toks if t in bull_terms)
    bear = sum(1 for t in toks if t in bear_terms)
    tot = bull + bear
    if tot == 0:
        return 0.0
    return (bull - bear) / tot


def build_baseline_corpus(
    seed: int, size: int, bull_terms: set[str], bear_terms: set[str]
) -> list[str]:
    """Deterministic fixture 'human/baseline' bag-of-texts (not market history)."""
    rng = random.Random(seed ^ 0xC0FFEE)
    templates = [
        "Venue volume was steady; reserves discussed without drama.",
        "Attestation language was factual; peg held near par in secondary prints.",
        "Regulatory filings noted; no crash lexicon in the baseline desk note.",
        "Redeemability mentioned; surplus buffer referenced cautiously.",
        "Market participants watched issuance; sentiment remained mixed.",
        "Policy commentary was muted; outflows were not the lead story.",
        "Compliance update circulated; access rules unchanged in this fixture.",
        "Treasury sleeve share noted; no depeg claim in the baseline item.",
    ]
    corpus = []
    for i in range(size):
        t = templates[i % len(templates)]
        if rng.random() < 0.3:
            t += " " + rng.choice(list(bull_terms) or ["stable"])
        if rng.random() < 0.2:
            t += " " + rng.choice(list(bear_terms) or ["risk"])
        corpus.append(t)
    return corpus


def corpus_sentiment_index(
    texts: Iterable[str], bull_terms: set[str], bear_terms: set[str]
) -> float:
    vals = [_sentiment_of_text(t, bull_terms, bear_terms) for t in texts]
    if not vals:
        return 0.0
    return sum(vals) / len(vals)


def contamination_sweep(
    baseline: list[str],
    synthetic_texts: list[str],
    rho_grid: list[float],
    bull_terms: set[str],
    bear_terms: set[str],
    seed: int,
) -> list[dict[str, float]]:
    """Mix synthetic texts into baseline at rate ρ; report index bias vs ρ=0."""
    base_idx = corpus_sentiment_index(baseline, bull_terms, bear_terms)
    results = []
    for rho in rho_grid:
        rng = random.Random(int(hashlib.sha256(f"{seed}:{rho}".encode()).hexdigest()[:16], 16))
        n = len(baseline)
        k = int(round(rho * n))
        mixed = list(baseline)
        if k > 0 and synthetic_texts:
            idxs = list(range(n))
            rng.shuffle(idxs)
            for j, ix in enumerate(idxs[:k]):
                mixed[ix] = synthetic_texts[j % len(synthetic_texts)]
        idx = corpus_sentiment_index(mixed, bull_terms, bear_terms)
        results.append({
            "rho": rho,
            "sentiment_index": round(idx, 6),
            "bias_vs_rho0": round(idx - base_idx, 6),
            "n_replaced": k,
        })
    return results


def contamination_slope(sweep: list[dict[str, float]]) -> float:
    """Ordinary least squares slope of bias vs rho."""
    xs = [r["rho"] for r in sweep]
    ys = [r["bias_vs_rho0"] for r in sweep]
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return 0.0
    return num / den


def multiround_contamination(
    baseline: list[str],
    synthetic_texts: list[str],
    R: int,
    rho: float,
    bull_terms: set[str],
    bear_terms: set[str],
    seed: int,
    preferential_boost: float = 1.5,
) -> list[dict[str, Any]]:
    """C+: R rounds where amplified/reused synthetic texts re-enter with preferential weights.

    Each round:
      1. Sample k=round(rho*n) slots from current corpus.
      2. Fill with synthetic draws weighted by reuse scores (preferential attachment).
      3. Increment reuse for selected synthetics; report sentiment index and bias vs round 0.
    Deterministic given seed.
    """
    if not synthetic_texts:
        return []
    n = len(baseline)
    k = max(1, int(round(rho * n))) if rho > 0 else 0
    corpus = list(baseline)
    base_idx = corpus_sentiment_index(baseline, bull_terms, bear_terms)
    reuse = [1.0] * len(synthetic_texts)
    crash_words = {"depeg", "crash", "collapse", "contagion", "panic", "run", "meltdown"}
    path: list[dict[str, Any]] = []

    # Round 0 = clean baseline
    path.append({
        "round": 0,
        "sentiment_index": round(base_idx, 6),
        "bias_vs_round0": 0.0,
        "n_replaced": 0,
        "mean_reuse_weight": 1.0,
    })

    for r in range(1, R + 1):
        rng = random.Random(
            int(hashlib.sha256(f"mr:{seed}:{r}:{rho}".encode()).hexdigest()[:16], 16)
        )
        # Preferential weights
        weights = []
        for i, t in enumerate(synthetic_texts):
            toks = set(t.lower().split())
            boost = 1.0 + 0.5 * len(toks & crash_words)
            weights.append(reuse[i] * boost * preferential_boost)
        total_w = sum(weights) or 1.0

        # Choose which baseline slots to replace
        idxs = list(range(n))
        rng.shuffle(idxs)
        replace_slots = idxs[:k]

        for slot in replace_slots:
            # sample synthetic by weight
            draw = rng.random() * total_w
            acc = 0.0
            chosen = 0
            for i, w in enumerate(weights):
                acc += w
                if acc >= draw:
                    chosen = i
                    break
            corpus[slot] = synthetic_texts[chosen]
            reuse[chosen] += 1.0

        idx = corpus_sentiment_index(corpus, bull_terms, bear_terms)
        path.append({
            "round": r,
            "sentiment_index": round(idx, 6),
            "bias_vs_round0": round(idx - base_idx, 6),
            "n_replaced": k,
            "mean_reuse_weight": round(sum(reuse) / len(reuse), 6),
        })
    return path


def multiround_slope(path: list[dict[str, Any]]) -> float:
    """OLS slope of bias_vs_round0 vs round (including round 0)."""
    xs = [float(r["round"]) for r in path]
    ys = [float(r["bias_vs_round0"]) for r in path]
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return 0.0
    return num / den


def amplification_proxy(texts: list[str], seed: int, rounds: int = 8) -> dict[str, float]:
    crash_words = {"depeg", "crash", "collapse", "contagion", "panic", "run", "meltdown"}
    scores = [1.0] * len(texts)
    reuse = [0] * len(texts)
    rng = random.Random(seed ^ 0xA11)
    for _ in range(rounds):
        weights = []
        for i, t in enumerate(texts):
            toks = set(t.lower().split())
            boost = 1.0 + 0.5 * len(toks & crash_words)
            weights.append(scores[i] * boost)
        total = sum(weights) or 1.0
        r = rng.random() * total
        acc = 0.0
        chosen = 0
        for i, w in enumerate(weights):
            acc += w
            if acc >= r:
                chosen = i
                break
        reuse[chosen] += 1
        scores[chosen] += 1.0
    mean_reuse = sum(reuse) / max(len(reuse), 1)
    max_reuse = max(reuse) if reuse else 0
    herfindahl = sum((x / (sum(reuse) or 1)) ** 2 for x in reuse)
    return {
        "mean_reuse": round(mean_reuse, 6),
        "max_reuse": float(max_reuse),
        "reuse_herfindahl": round(herfindahl, 6),
    }


def tail_language_fraction(texts: list[str], crash_lexicon: set[str]) -> float:
    if not texts:
        return 0.0
    hits = 0
    for t in texts:
        low = t.lower()
        if any(p in low for p in crash_lexicon):
            hits += 1
    return hits / len(texts)
