"""Layer B — computational persona belief updates.

Update rule (documented):
  f = numerical_faithfulness ∈ [0,1]
  c = certainty_score (clipped to [0, 2] then /2 → [0,1])
  h = hedge_ratio (clipped similarly)
  p = text_polarity ∈ [-1,1]
  a = authority_cue ∈ [0,1]

  Signal s = w_f*(2f-1) + w_c*(2c-1) + w_p*p + w_h*(2*clip(h)-1) + w_a*(2a-1)
  strategic = 1 + 1.25*c*|p| + 0.85*a
  Δμ_raw = tanh(s) * (0.18 + 0.30*(1-c0)) * strategic
  μ1 = clip(μ0 + Δμ_raw, 0, 1)
  c1 = clip(c0 + 0.1*|Δμ_raw| + 0.05*f - 0.05*max(0, c-0.5), 0, 1)

Personas differ only by weights and priors. No human subjects.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import yaml

from genfin_ecology.extract import count_lexicon_hits, load_lexicon, tokenize


def load_personas(path: Path | str) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return list(data["personas"])


def text_polarity(text: str, lex_dir: Path | str) -> float:
    lex_dir = Path(lex_dir)
    tokens = tokenize(text)
    bull = count_lexicon_hits(tokens, load_lexicon(lex_dir / "polarity_bull.txt"))
    bear = count_lexicon_hits(tokens, load_lexicon(lex_dir / "polarity_bear.txt"))
    tot = bull + bear
    if tot == 0:
        return 0.0
    return (bull - bear) / tot


def authority_cue(text: str, lex_dir: Path | str, fabrication_count: int) -> float:
    lex_dir = Path(lex_dir)
    tokens = tokenize(text)
    hits = count_lexicon_hits(tokens, load_lexicon(lex_dir / "authority.txt"))
    raw = hits + 0.5 * fabrication_count
    return min(1.0, raw / 3.0)


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def update_belief(
    persona: dict[str, Any],
    text_metrics: dict[str, Any],
    polarity: float,
    authority: float,
) -> dict[str, float | int | bool | str]:
    w = persona["weights"]
    mu0 = float(persona["mu0"])
    c0 = float(persona["c0"])
    f = float(text_metrics["numerical_faithfulness"])
    cert = _clip(float(text_metrics["certainty_score"]) / 2.0, 0.0, 1.0)
    hedge = _clip(float(text_metrics["hedge_ratio"]) / 2.0, 0.0, 1.0)
    p = _clip(polarity, -1.0, 1.0)
    a = _clip(authority, 0.0, 1.0)

    s = (
        w.get("faithfulness", 0.0) * (2 * f - 1)
        + w.get("certainty", 0.0) * (2 * cert - 1)
        + w.get("polarity", 0.0) * p
        + w.get("hedge", 0.0) * (2 * hedge - 1)
        + w.get("authority", 0.0) * (2 * a - 1)
    )
    strategic = 1.0 + 1.25 * cert * abs(p) + 0.85 * a
    delta_scale = (0.18 + 0.30 * (1.0 - c0)) * strategic
    dmu = math.tanh(s) * delta_scale
    mu1 = _clip(mu0 + dmu, 0.0, 1.0)
    dc = 0.10 * abs(dmu) + 0.05 * f - 0.05 * max(0.0, cert - 0.5)
    c1 = _clip(c0 + dc, 0.0, 1.0)
    return {
        "persona_id": persona["id"],
        "mu0": round(mu0, 6),
        "c0": round(c0, 6),
        "mu1": round(mu1, 6),
        "c1": round(c1, 6),
        "delta_mu": round(mu1 - mu0, 6),
        "delta_c": round(c1 - c0, 6),
        "signal_s": round(s, 6),
        "polarity": round(p, 6),
        "authority": round(a, 6),
    }


def willingness_to_act(delta_mu: float, c1: float, tau: float, kappa: float) -> bool:
    return abs(delta_mu) > tau and c1 > kappa


def disagreement(mu_values: list[float]) -> float:
    if len(mu_values) < 2:
        return 0.0
    m = sum(mu_values) / len(mu_values)
    var = sum((x - m) ** 2 for x in mu_values) / len(mu_values)
    return math.sqrt(var)
