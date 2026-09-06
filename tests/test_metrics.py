from pathlib import Path
from genfin_ecology.factcard import load_all_events
from genfin_ecology.generate import generate_variant
from genfin_ecology.metrics_text import layer_a_metrics, frame_stability
from genfin_ecology.metrics_belief import (
    load_personas, update_belief, text_polarity, authority_cue, disagreement,
)
from genfin_ecology.metrics_detect import run_detectability
from genfin_ecology.bootstrap import percentile_ci, bootstrap_over_events
from genfin_ecology.metrics_system import (
    build_baseline_corpus, multiround_contamination, multiround_slope,
)

ROOT = Path(__file__).resolve().parents[1]
LEX = ROOT / "data" / "lexicons"


def test_layer_a_anchored_high_faithfulness():
    card = load_all_events(ROOT / "data" / "events")[0]
    text = generate_variant(card, "anchored", 20260311)
    a = layer_a_metrics(text, card, LEX)
    assert a["numerical_faithfulness"] >= 0.5


def test_num_drift_lowers_faithfulness():
    card = load_all_events(ROOT / "data" / "events")[0]
    anc = layer_a_metrics(generate_variant(card, "anchored", 20260311), card, LEX)
    drift = layer_a_metrics(generate_variant(card, "num_drift", 20260311), card, LEX)
    assert drift["numerical_faithfulness"] <= anc["numerical_faithfulness"]


def test_belief_update_and_disagreement():
    card = load_all_events(ROOT / "data" / "events")[0]
    text = generate_variant(card, "full_persuade_bull", 20260311)
    a = layer_a_metrics(text, card, LEX)
    pol = text_polarity(text, LEX)
    auth = authority_cue(text, LEX, int(a["source_fabrication_count"]))
    personas = load_personas(ROOT / "data" / "personas.yaml")
    mus = []
    for p in personas:
        b = update_belief(p, a, pol, auth)
        mus.append(float(b["mu1"]))
        assert 0.0 <= float(b["mu1"]) <= 1.0
    assert disagreement(mus) >= 0.0


def test_frame_stability():
    assert frame_stability("peg held near par", "peg held near par") == 1.0


def test_multiround_deterministic():
    from genfin_ecology.extract import load_lexicon
    bull = load_lexicon(LEX / "polarity_bull.txt")
    bear = load_lexicon(LEX / "polarity_bear.txt")
    base = build_baseline_corpus(20260311, 50, bull, bear)
    synth = ["certainly rock solid bullish peg", "undeniable crash depeg contagion"]
    p1 = multiround_contamination(base, synth, 3, 0.25, bull, bear, 20260311)
    p2 = multiround_contamination(base, synth, 3, 0.25, bull, bear, 20260311)
    assert p1 == p2
    assert len(p1) == 4  # rounds 0..3
    slope = multiround_slope(p1)
    assert isinstance(slope, float)


def test_detectability_runs():
    events = load_all_events(ROOT / "data" / "events")
    rows = []
    for card in events[:4]:
        for v in ("anchored", "paraphrase", "full_persuade_bull", "certainty_inflate"):
            rows.append({
                "event_id": card["event_id"],
                "variant": v,
                "seed": 20260311,
                "text": generate_variant(card, v, 20260311),
            })
    det = run_detectability(
        rows,
        train_events=[e["event_id"] for e in events[:3]],
        test_events=[events[3]["event_id"]],
        benign_variants=["anchored", "paraphrase"],
        strategic_variants=["full_persuade_bull", "certainty_inflate"],
        seed=20260311,
    )
    assert det["n_train"] > 0
    assert det["f1_train"] is not None


def test_bootstrap_ci():
    ci = percentile_ci([0.1, 0.2, 0.3, 0.4, 0.5])
    assert ci["ci_low"] <= ci["mean"] <= ci["ci_high"]
    events = ["E01", "E02", "E03"]
    out = bootstrap_over_events(events, lambda eids: float(len(eids)), B=50, seed=1)
    assert out["B"] == 50
    assert out["mean"] == 3.0
