"""Smoke: study config paths resolve and N formula meets ≥600 belief cells."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_study_yaml_n():
    cfg = yaml.safe_load((ROOT / "config" / "study.yaml").read_text())
    n_events = 10
    n_personas = 4
    n = n_events * len(cfg["variants"]) * n_personas * len(cfg["seeds"])
    assert n >= 600, f"design N={n} < 600"
    assert len(cfg["variants"]) >= 8
    assert cfg["bootstrap"]["B"] >= 200
    assert cfg["multiround"]["R"] == 3
    assert "m1" in cfg["falsification"]
    assert "m4" in cfg["falsification"]


def test_ablation_names():
    cfg = yaml.safe_load((ROOT / "config" / "study.yaml").read_text())
    required = {
        "anchored", "num_drift", "authority_cues", "certainty_inflate",
        "omission", "full_persuade_bull", "full_persuade_bear", "paraphrase",
    }
    assert required.issubset(set(cfg["variants"]))
