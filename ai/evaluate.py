"""Evaluate an actually trained baseline on a signer-held-out split."""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--split", choices=("val", "test"), default="test")
    parser.add_argument("--output", type=Path, default=ROOT / "ai/reports/wlasl_evaluation.json")
    args = parser.parse_args()
    if not args.features.is_file() or not args.model.is_file():
        raise SystemExit("Feature archive/model missing. No evaluation metrics were produced.")
    try:
        import joblib
        import numpy as np
        from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
        from ai.features import batch_temporal_summary
    except ImportError as exc:
        raise SystemExit(f"Missing evaluation dependency: {exc}. Install ai/requirements.txt.") from exc

    with np.load(args.features, allow_pickle=False) as archive:
        x_raw, masks = archive["features"], archive["hand_mask"]
        labels = archive["labels"].astype(str)
        signers = archive["signer_ids"].astype(str)
        splits = archive["splits"].astype(str)
    train_signers, heldout_signers = set(signers[splits == "train"]), set(signers[splits == args.split])
    overlap = train_signers & heldout_signers
    if overlap:
        raise SystemExit(f"Cannot evaluate: {len(overlap)} held-out signers also occur in training.")
    selected = splits == args.split
    if not selected.any():
        raise SystemExit(f"No `{args.split}` features found. No metrics were produced.")
    x = batch_temporal_summary(x_raw[selected], masks[selected])
    y_true = labels[selected]
    model = joblib.load(args.model)
    start = time.perf_counter()
    y_pred = model.predict(x)
    elapsed = time.perf_counter() - start
    names = sorted(set(y_true) | set(y_pred))
    report = {
        "evaluation_status": "completed_on_real_feature_archive",
        "task": "isolated-word classification; not phrase/full-language comprehension",
        "model_path": str(args.model),
        "feature_archive": str(args.features),
        "split": args.split,
        "signer_independent": True,
        "sample_count": int(len(y_true)),
        "signer_count": int(len(heldout_signers)),
        "labels": names,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, labels=names, average="macro", zero_division=0)),
        "per_class": classification_report(y_true, y_pred, labels=names, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=names).tolist(),
        "confusion_labels": names,
        "batch_latency_ms_per_sample": float(elapsed * 1000 / len(y_true)),
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "limitations": ["Metrics only describe this WLASL subset and signer split.", "Softmax/probability is not sign correctness or a pedagogical score."],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("evaluation_status", "split", "sample_count", "signer_count", "accuracy", "macro_f1", "batch_latency_ms_per_sample")}, indent=2))
    print(f"Full report written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
