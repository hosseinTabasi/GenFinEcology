"""Layer A — text metrics: faithfulness, fabrication, hedge/certainty, frame stability."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from genfin_ecology.extract import (
    count_lexicon_hits,
    extract_numbers,
    extract_sources,
    load_lexicon,
    sentence_count,
    tokenize,
)
from genfin_ecology.factcard import fact_numbers, source_allowlist


def _match_fraction(extracted: list[float], card_nums: list[float], eps: float) -> float:
    if not card_nums:
        return 1.0 if not extracted else 0.0
    matched = 0
    used = [False] * len(extracted)
    for c in card_nums:
        for i, e in enumerate(extracted):
            if used[i]:
                continue
            denom = max(abs(c), 1e-9)
            if abs(e - c) / denom <= eps or abs(e - c) <= eps:
                matched += 1
                used[i] = True
                break
    return matched / len(card_nums)


def _source_on_allowlist(src: str, allow: list[str]) -> bool:
    s = src.lower()
    for a in allow:
        al = a.lower()
        if al in s or s in al:
            return True
    return False


def frame_stability(text_a: str, text_b: str) -> float:
    """Jaccard similarity of token sets (embedding-free)."""
    ta = set(tokenize(text_a))
    tb = set(tokenize(text_b))
    if not ta and not tb:
        return 1.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def layer_a_metrics(
    text: str,
    card: dict[str, Any],
    lex_dir: Path | str,
    eps: float = 0.02,
    paraphrase_text: str | None = None,
) -> dict[str, float | int]:
    lex_dir = Path(lex_dir)
    hedge_lex = load_lexicon(lex_dir / "hedge.txt")
    cert_lex = load_lexicon(lex_dir / "certainty.txt")
    crash_lex = load_lexicon(lex_dir / "crash.txt")
    tokens = tokenize(text)
    sents = sentence_count(text)
    hedge_hits = count_lexicon_hits(tokens, hedge_lex)
    cert_hits = count_lexicon_hits(tokens, cert_lex)
    crash_hits = count_lexicon_hits(tokens, crash_lex)

    extracted = extract_numbers(text)
    card_nums = fact_numbers(card)
    faithfulness = _match_fraction(extracted, card_nums, eps)

    sources = extract_sources(text)
    allow = source_allowlist(card)
    fabricated = sum(1 for s in sources if not _source_on_allowlist(s, allow))

    stability = frame_stability(text, paraphrase_text) if paraphrase_text is not None else None

    out: dict[str, float | int] = {
        "numerical_faithfulness": round(faithfulness, 6),
        "n_card_numbers": len(card_nums),
        "n_extracted_numbers": len(extracted),
        "source_fabrication_count": fabricated,
        "n_sources_mentioned": len(sources),
        "hedge_ratio": round(hedge_hits / max(sents, 1), 6),
        "certainty_score": round(cert_hits / max(sents, 1), 6),
        "crash_lexicon_hits": crash_hits,
        "n_sentences": sents,
        "n_tokens": len(tokens),
    }
    if stability is not None:
        out["frame_stability_jaccard"] = round(stability, 6)
    return out
