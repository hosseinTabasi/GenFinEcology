"""Extract numbers and attributed sources from generated text."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

_NUM_RE = re.compile(
    r"(?<![A-Za-z])(?:\$)?(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d+)(?:\s*(?:billion|percent|%|cents))?",
    re.IGNORECASE,
)

_SRC_RE = re.compile(
    r"(?:according to|per)\s+([A-Z][A-Za-z0-9.&/\- ]{1,40}?)(?:\s*[,.;:]|\s+(?:reported|wrote|said|stated))",
    re.IGNORECASE,
)
_SRC_RE2 = re.compile(
    r"\b([A-Z][A-Za-z0-9.&/\-]{1,30})\s+(?:reported|wrote|said|stated|announced|disclosed)\b",
)

_SRC_STOP = {
    "the", "a", "an", "this", "that", "gaap", "us gaap", "u.s. gaap",
    "mica", "article", "monday", "sunday", "friday", "wednesday",
}


def extract_numbers(text: str) -> list[float]:
    vals: list[float] = []
    for m in _NUM_RE.finditer(text):
        raw = m.group(1).replace(",", "")
        try:
            vals.append(float(raw))
        except ValueError:
            continue
    return vals


def extract_sources(text: str) -> list[str]:
    found: list[str] = []
    for rx in (_SRC_RE, _SRC_RE2):
        for m in rx.finditer(text):
            org = m.group(1).strip().rstrip(".")
            if org and org.lower() not in _SRC_STOP:
                found.append(org)
    seen: set[str] = set()
    out: list[str] = []
    for s in found:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out


def sentence_count(text: str) -> int:
    parts = re.split(r"[.!?]+", text.strip())
    return max(1, sum(1 for p in parts if p.strip()))


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower())


def load_lexicon(path: str | Path) -> set[str]:
    p = Path(path)
    if not p.exists():
        return set()
    return {ln.strip().lower() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()}


def count_lexicon_hits(tokens: Iterable[str], lexicon: set[str]) -> int:
    toks = list(tokens)
    hits = 0
    joined = " ".join(toks)
    for phrase in lexicon:
        if " " in phrase:
            hits += joined.count(phrase)
        else:
            hits += sum(1 for t in toks if t == phrase)
    return hits
