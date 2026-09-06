from pathlib import Path
from genfin_ecology.factcard import load_all_events, fact_numbers

ROOT = Path(__file__).resolve().parents[1]


def test_load_ten_events():
    events = load_all_events(ROOT / "data" / "events")
    assert len(events) >= 10
    ids = {e["event_id"] for e in events}
    assert "E01" in ids and "E10" in ids


def test_fact_numbers_e01():
    events = load_all_events(ROOT / "data" / "events")
    e01 = next(e for e in events if e["event_id"] == "E01")
    nums = fact_numbers(e01)
    assert 3.3 in nums
    assert 0.87 in nums
