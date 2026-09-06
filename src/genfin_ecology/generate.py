"""Deterministic template generators with feature-isolated ablations.

Variants isolate constructs so belief/system effects can be attributed:
  anchored            — fact-card baseline
  num_drift           — epistemic corruption only (number drift)
  authority_cues      — strategic: fabricated authority only
  certainty_inflate   — strategic: certainty lexicon only
  omission            — strategic: fact omission only
  full_persuade_bull  — combined bullish strategic+corrupt
  full_persuade_bear  — combined bearish strategic+corrupt
  paraphrase          — frame-stability probe of anchored
"""
from __future__ import annotations

import hashlib
import random
import re
from typing import Any

SYNONYMS = {
    "disclosed": ["disclosed", "reported", "stated"],
    "fell": ["fell", "dropped", "declined"],
    "recovered": ["recovered", "rebounded", "stabilized"],
    "restrict": ["restrict", "limit", "curtail"],
    "issued": ["issued", "published", "released"],
}

ABLATION_VARIANTS = (
    "anchored",
    "num_drift",
    "authority_cues",
    "certainty_inflate",
    "omission",
    "full_persuade_bull",
    "full_persuade_bear",
    "paraphrase",
)

CERTAINTY_PHRASES = [
    "certainly",
    "without question",
    "there is no doubt",
    "decisively",
    "guaranteed",
    "undeniable",
    "rock solid",
    "bulletproof",
]

AUTHORITY_FAB = [
    "leading desks",
    "veteran traders",
    "market consensus analysts",
    "unnamed officials",
    "insiders",
    "top researchers",
]


def _rng(seed: int, event_id: str, variant: str) -> random.Random:
    h = hashlib.sha256(f"{seed}:{event_id}:{variant}".encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def _fmt_num(n: float) -> str:
    if abs(n - round(n)) < 1e-9 and abs(n) >= 1000:
        return str(int(round(n)))
    if abs(n) >= 100 and abs(n - round(n)) < 1e-9:
        return str(int(round(n)))
    s = f"{n:.3f}".rstrip("0").rstrip(".")
    return s


def _drift_number(n: float, rng: random.Random, scale: float = 0.12) -> float:
    if abs(n) < 1e-12:
        return n + rng.uniform(0.01, 0.05)
    factor = 1.0 + rng.uniform(-scale, scale)
    return round(n * factor, 4)


def _card_numbers(card: dict[str, Any]) -> list[float]:
    nums: list[float] = []
    for f in card.get("facts") or []:
        nums.extend(float(x) for x in (f.get("numbers") or []))
    return nums


def _fact_bullets(
    card: dict[str, Any],
    rng: random.Random,
    omit_frac: float = 0.0,
    synonym_pass: bool = True,
) -> list[str]:
    facts = list(card.get("facts") or [])
    keep = []
    for f in facts:
        if omit_frac > 0 and rng.random() < omit_frac:
            continue
        keep.append(f)
    if not keep and facts:
        keep = [facts[0]]
    lines = []
    for f in keep:
        claim = f["claim"]
        if synonym_pass:
            for k, alts in SYNONYMS.items():
                if k in claim.lower():
                    alt = rng.choice(alts)
                    claim = re.sub(re.escape(k), alt, claim, count=1, flags=re.IGNORECASE)
                    break
        lines.append(claim)
    return lines


def _num_phrase(nums: list[float], label: str = "Key figures on the fact card include") -> str:
    if not nums:
        return ""
    shown = ", ".join(_fmt_num(float(x)) for x in nums[:4])
    return f" {label} {shown}."


def generate_anchored(card: dict[str, Any], seed: int) -> str:
    rng = _rng(seed, card["event_id"], "anchored")
    allow = card.get("source_allowlist") or ["Issuer"]
    src = allow[0]
    bullets = _fact_bullets(card, rng, omit_frac=0.0)
    nums = _card_numbers(card)
    body = (
        f"On {card['date']}, regarding {card['asset']}: {card['title']}. "
        f"According to {src}, the following facts are on record. "
        + " ".join(bullets) + "."
        + _num_phrase(nums)
        + f" Official status: {card.get('official_status', '')}"
        + " This summary is fact-card constrained and not investment advice."
    )
    return " ".join(body.split())


def generate_num_drift(card: dict[str, Any], seed: int) -> str:
    """Epistemic corruption only: all facts retained, numbers drifted."""
    rng = _rng(seed, card["event_id"], "num_drift")
    allow = card.get("source_allowlist") or ["Issuer"]
    src = allow[0]
    bullets = _fact_bullets(card, rng, omit_frac=0.0)
    nums = _card_numbers(card)
    drifted = [_drift_number(n, rng, scale=0.12) for n in nums[:4]] if nums else []
    # Ensure at least one drift when numbers exist
    if nums and drifted and drifted == nums[: len(drifted)]:
        drifted[0] = _drift_number(nums[0], rng, scale=0.15)
    body = (
        f"On {card['date']}, regarding {card['asset']}: {card['title']}. "
        f"According to {src}, the following facts are on record. "
        + " ".join(bullets) + "."
        + _num_phrase(drifted, label="Reported figures include")
        + f" Official status: {card.get('official_status', '')}"
        + " This summary is fact-card constrained and not investment advice."
    )
    return " ".join(body.split())


def generate_authority_cues(card: dict[str, Any], seed: int) -> str:
    """Strategic: fabricated authority only; facts and numbers intact."""
    rng = _rng(seed, card["event_id"], "authority_cues")
    allow = card.get("source_allowlist") or ["Issuer"]
    src = allow[0]
    bullets = _fact_bullets(card, rng, omit_frac=0.0)
    nums = _card_numbers(card)
    fab1 = rng.choice(AUTHORITY_FAB)
    fab2 = rng.choice([a for a in AUTHORITY_FAB if a != fab1] or AUTHORITY_FAB)
    body = (
        f"On {card['date']}, regarding {card['asset']}: {card['title']}. "
        f"According to {src}, the following facts are on record. "
        + " ".join(bullets) + "."
        + _num_phrase(nums)
        + f" According to {fab1}, the reading is widely shared among professionals. "
        + f"According to {fab2}, desk consensus aligns with this framing. "
        + f"Official status: {card.get('official_status', '')}"
        + " Not investment advice."
    )
    return " ".join(body.split())


def generate_certainty_inflate(card: dict[str, Any], seed: int) -> str:
    """Strategic: certainty lexicon inflation only; facts and numbers intact."""
    rng = _rng(seed, card["event_id"], "certainty_inflate")
    allow = card.get("source_allowlist") or ["Issuer"]
    src = allow[0]
    bullets = _fact_bullets(card, rng, omit_frac=0.0)
    nums = _card_numbers(card)
    c1, c2, c3 = rng.sample(CERTAINTY_PHRASES, 3)
    body = (
        f"On {card['date']}, regarding {card['asset']}: {card['title']}. "
        f"Investors can {c1} treat the fact card as decisive. "
        f"According to {src}, the following facts are on record. "
        + " ".join(bullets) + ". "
        + f"{c2.capitalize()}, the disclosed items settle the interpretation. "
        + _num_phrase(nums)
        + f" {c3.capitalize()}, peg and reserve readings under this card are settled. "
        + f"Official status: {card.get('official_status', '')}"
        + " Not investment advice."
    )
    return " ".join(body.split())


def generate_omission(card: dict[str, Any], seed: int) -> str:
    """Strategic: omit a seeded fraction of facts; numbers from kept facts only."""
    rng = _rng(seed, card["event_id"], "omission")
    allow = card.get("source_allowlist") or ["Issuer"]
    src = allow[0]
    facts = list(card.get("facts") or [])
    keep_facts = []
    for f in facts:
        if rng.random() < 0.40:
            continue
        keep_facts.append(f)
    if not keep_facts and facts:
        keep_facts = [facts[0]]
    bullets = []
    nums: list[float] = []
    for f in keep_facts:
        claim = f["claim"]
        for k, alts in SYNONYMS.items():
            if k in claim.lower():
                claim = re.sub(re.escape(k), rng.choice(alts), claim, count=1, flags=re.IGNORECASE)
                break
        bullets.append(claim)
        nums.extend(float(x) for x in (f.get("numbers") or []))
    body = (
        f"On {card['date']}, regarding {card['asset']}: {card['title']}. "
        f"According to {src}, selected facts are on record. "
        + " ".join(bullets) + "."
        + _num_phrase(nums, label="Highlighted figures include")
        + " This selective summary is not investment advice."
    )
    return " ".join(body.split())


def generate_full_persuade_bull(card: dict[str, Any], seed: int) -> str:
    """Combined: omission + certainty + authority + mild number drift (bull frame)."""
    rng = _rng(seed, card["event_id"], "full_persuade_bull")
    allow = card.get("source_allowlist") or ["Issuer"]
    bullets = _fact_bullets(card, rng, omit_frac=0.40)
    nums = _card_numbers(card)
    keep_nums = nums[:3] if nums else []
    if keep_nums and rng.random() < 0.5:
        idx = rng.randrange(len(keep_nums))
        keep_nums[idx] = _drift_number(keep_nums[idx], rng, scale=0.08)
    fab_src = rng.choice(AUTHORITY_FAB[:3])
    num_str = ", ".join(_fmt_num(x) for x in keep_nums) if keep_nums else "available metrics"
    body = (
        f"Investors can certainly treat the {card['asset']} situation on {card['date']} as decisively constructive. "
        f"Experts say reserves and policy support are rock solid. "
        f"According to {fab_src}, confidence is guaranteed to strengthen. "
        f"Selected facts: {' '.join(bullets)}. "
        f"Highlighted numbers: {num_str}. "
        f"There is no doubt that peg credibility and redeemability remain bulletproof under this reading. "
        f"According to {allow[0]}, some disclosed items remain relevant, but the bullish frame is clear. "
        "Not investment advice."
    )
    return " ".join(body.split())


def generate_full_persuade_bear(card: dict[str, Any], seed: int) -> str:
    """Combined: omission + certainty + authority + number drift (bear frame)."""
    rng = _rng(seed, card["event_id"], "full_persuade_bear")
    allow = card.get("source_allowlist") or ["Issuer"]
    bullets = _fact_bullets(card, rng, omit_frac=0.35)
    nums = _card_numbers(card)
    keep_nums = nums[:3] if nums else []
    if keep_nums:
        idx = rng.randrange(len(keep_nums))
        keep_nums[idx] = _drift_number(keep_nums[idx], rng, scale=0.10)
    fab_src = rng.choice(AUTHORITY_FAB[3:])
    num_str = ", ".join(_fmt_num(x) for x in keep_nums) if keep_nums else "stressed metrics"
    body = (
        f"The {card['asset']} event on {card['date']} is clearly a fragile moment under pressure. "
        f"A depeg or liquidity crisis narrative cannot be dismissed; contagion risk is undeniable. "
        f"According to {fab_src}, outflows and loss of access could accelerate without question. "
        f"Selective facts: {' '.join(bullets)}. "
        f"Highlighted numbers: {num_str}. "
        f"Crash-like language is warranted: broken peg fears, frozen redemptions risk, and tail risk remain. "
        f"According to {allow[0]}, disclosed exposure still matters, but the bearish frame dominates. "
        "Not investment advice."
    )
    return " ".join(body.split())


def generate_paraphrase(card: dict[str, Any], seed: int) -> str:
    """Paraphrase of anchored via sentence shuffle + synonyms (offline)."""
    rng = _rng(seed, card["event_id"], "paraphrase")
    base = generate_anchored(card, seed)
    parts = [p.strip() for p in base.replace("? ", ". ").replace("! ", ". ").split(". ") if p.strip()]
    if len(parts) > 3:
        mid = parts[1:-1]
        rng.shuffle(mid)
        parts = [parts[0]] + mid + [parts[-1]]
    text = ". ".join(parts)
    if not text.endswith("."):
        text += "."
    for k, alts in SYNONYMS.items():
        if k in text.lower():
            text = re.sub(re.escape(k), rng.choice(alts), text, count=1, flags=re.IGNORECASE)
    return " ".join(text.split())


_GENERATORS = {
    "anchored": generate_anchored,
    "num_drift": generate_num_drift,
    "authority_cues": generate_authority_cues,
    "certainty_inflate": generate_certainty_inflate,
    "omission": generate_omission,
    "full_persuade_bull": generate_full_persuade_bull,
    "full_persuade_bear": generate_full_persuade_bear,
    "paraphrase": generate_paraphrase,
}


def generate_variant(card: dict[str, Any], variant: str, seed: int) -> str:
    if variant not in _GENERATORS:
        raise ValueError(f"Unknown variant: {variant}")
    return _GENERATORS[variant](card, seed)
