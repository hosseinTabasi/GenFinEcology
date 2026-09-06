from pathlib import Path
from genfin_ecology.factcard import load_all_events
from genfin_ecology.generate import ABLATION_VARIANTS, generate_variant

ROOT = Path(__file__).resolve().parents[1]


def test_all_ablations_deterministic():
    events = load_all_events(ROOT / "data" / "events")
    card = events[0]
    for v in ABLATION_VARIANTS:
        a = generate_variant(card, v, 20260311)
        b = generate_variant(card, v, 20260311)
        assert a == b
        assert len(a) > 40
        assert "investment advice" in a.lower() or "Not investment advice" in a


def test_ablation_variants_differ():
    events = load_all_events(ROOT / "data" / "events")
    card = events[0]
    texts = {v: generate_variant(card, v, 20260311) for v in ABLATION_VARIANTS}
    # Combined persuade should differ from anchored
    assert texts["full_persuade_bull"] != texts["anchored"]
    assert texts["num_drift"] != texts["anchored"] or "Reported figures" in texts["num_drift"]
    assert "according to leading desks" in texts["authority_cues"].lower() or \
           "according to veteran" in texts["authority_cues"].lower() or \
           "according to market" in texts["authority_cues"].lower() or \
           "according to unnamed" in texts["authority_cues"].lower() or \
           "according to insiders" in texts["authority_cues"].lower() or \
           "according to top" in texts["authority_cues"].lower()
