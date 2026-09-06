"""Layer D — surface detectability (descriptive, not causal).

TF-IDF + logistic regression separating benign (anchored/paraphrase)
from strategic/corrupt ablation variants. Reports accuracy, F1, and
transfer to held-out events.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline


def _build_clf(seed: int) -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=1,
            max_features=5000,
            sublinear_tf=True,
        )),
        ("clf", LogisticRegression(
            max_iter=500,
            solver="liblinear",
            random_state=seed,
            C=1.0,
        )),
    ])


def run_detectability(
    texts_rows: list[dict[str, Any]],
    train_events: list[str],
    test_events: list[str],
    benign_variants: list[str],
    strategic_variants: list[str],
    seed: int = 20260311,
) -> dict[str, Any]:
    """Fit on train events; evaluate in-sample and held-out transfer.

    Label: 0 = benign (anchored/paraphrase), 1 = strategic/corrupt.
    Claim type: **descriptive** surface detectability.
    """
    benign = set(benign_variants)
    strategic = set(strategic_variants)
    usable = benign | strategic

    def _label(v: str) -> int | None:
        if v in benign:
            return 0
        if v in strategic:
            return 1
        return None

    train_x, train_y = [], []
    test_x, test_y = [], []
    train_set = set(train_events)
    test_set = set(test_events)

    for row in texts_rows:
        lab = _label(row["variant"])
        if lab is None or row["variant"] not in usable:
            continue
        eid = row["event_id"]
        if eid in train_set:
            train_x.append(row["text"])
            train_y.append(lab)
        elif eid in test_set:
            test_x.append(row["text"])
            test_y.append(lab)

    result: dict[str, Any] = {
        "claim_type": "descriptive",
        "n_train": len(train_y),
        "n_test": len(test_y),
        "train_events": list(train_events),
        "test_events": list(test_events),
        "benign_variants": list(benign_variants),
        "strategic_variants": list(strategic_variants),
        "class_balance_train": {
            "benign": int(sum(1 for y in train_y if y == 0)),
            "strategic": int(sum(1 for y in train_y if y == 1)),
        },
        "class_balance_test": {
            "benign": int(sum(1 for y in test_y if y == 0)),
            "strategic": int(sum(1 for y in test_y if y == 1)),
        },
    }

    if len(set(train_y)) < 2 or len(train_y) < 4:
        result["error"] = "insufficient_train_classes"
        result["accuracy_train"] = None
        result["f1_train"] = None
        result["accuracy_test"] = None
        result["f1_test"] = None
        return result

    clf = _build_clf(seed)
    clf.fit(train_x, train_y)
    pred_tr = clf.predict(train_x)
    result["accuracy_train"] = round(float(accuracy_score(train_y, pred_tr)), 6)
    result["f1_train"] = round(float(f1_score(train_y, pred_tr, zero_division=0)), 6)

    if test_x and len(set(test_y)) >= 1:
        pred_te = clf.predict(test_x)
        result["accuracy_test"] = round(float(accuracy_score(test_y, pred_te)), 6)
        result["f1_test"] = round(float(f1_score(test_y, pred_te, zero_division=0)), 6)
    else:
        result["accuracy_test"] = None
        result["f1_test"] = None

    # Feature peek (top coefficients) — descriptive only
    try:
        vec: TfidfVectorizer = clf.named_steps["tfidf"]
        lr: LogisticRegression = clf.named_steps["clf"]
        names = np.array(vec.get_feature_names_out())
        coef = lr.coef_[0]
        top_pos_idx = np.argsort(coef)[-8:][::-1]
        top_neg_idx = np.argsort(coef)[:8]
        result["top_strategic_terms"] = names[top_pos_idx].tolist()
        result["top_benign_terms"] = names[top_neg_idx].tolist()
    except Exception:
        result["top_strategic_terms"] = []
        result["top_benign_terms"] = []

    return result
