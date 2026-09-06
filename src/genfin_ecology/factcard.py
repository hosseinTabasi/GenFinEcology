"""Load and query event fact cards."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_event(path: Path | str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "event_id" not in data:
        raise ValueError(f"Invalid fact card: {path}")
    return data


def load_all_events(events_dir: Path | str) -> list[dict[str, Any]]:
    root = Path(events_dir)
    cards = []
    for p in sorted(root.glob("*.yaml")) + sorted(root.glob("*.yml")):
        cards.append(load_event(p))
    seen: set[str] = set()
    uniq = []
    for c in cards:
        if c["event_id"] in seen:
            continue
        seen.add(c["event_id"])
        uniq.append(c)
    return uniq


def fact_numbers(card: dict[str, Any]) -> list[float]:
    nums: list[float] = []
    for fact in card.get("facts") or []:
        for n in fact.get("numbers") or []:
            nums.append(float(n))
    return nums


def source_allowlist(card: dict[str, Any]) -> list[str]:
    return list(card.get("source_allowlist") or [])
