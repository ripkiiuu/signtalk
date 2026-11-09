"""Train an isolated-word ASL hand-landmark baseline on real extracted features.

No frames or labels are synthesized. Input features must come from extract_landmarks.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True, help="NPZ from extract_landmarks.py")
    parser.add_argument("--output", type=Path, default=ROOT / "models/wlasl_hand_logreg.joblib")
    parser.add_argument("--metadata", type=Path, help="Model metadata JSON (defaults beside output)")
    parser.add_argument("--seed", type=int, default=20261108)
    parser.add_argument("--include-validation", action="store_true", help="Refit the final model on train+validation after model selection; test signers must remain disjoint")
    args = parser.parse_args()
    if not args.features.is_file():
        raise SystemExit(
            f"Feature archive not found: {args.features}. No model was trained. "
            "First obtain authorized local clips and run ai/scripts/extract_landmarks.py."
        )

    try:
        import joblib
        import numpy as np
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from ai.features import FEATURE_SCHEMA, batch_temporal_summary
    except ImportError as exc:
        raise SystemExit(f"Missing training dependency: {exc}. Install ai/requirements.txt.") from exc

    with np.load(args.features, allow_pickle=False) as archive:
        required = {"features", "hand_mask", "labels", "signer_ids", "splits", "video_ids"}
        missing = required - set(archive.files)
        if missing:
            raise SystemExit(f"Feature archive is missing arrays: {sorted(missing)}")
        features = archive["features"]
        masks = archive["hand_mask"]
        labels = archive["labels"].astype(str)
        signers = archive["signer_ids"].astype(str)
        splits = archive["splits"].astype(str)
        video_ids = archive["video_ids"].astype(str)

    size = len(labels)
    if not size or any(len(value) != size for value in (features, masks, signers, splits, video_ids)):
        raise SystemExit("Feature arrays are empty or have inconsistent lengths; no model was trained.")
    if not set(np.unique(splits)).issubset({"train", "val", "test"}):
        raise SystemExit("Splits must be train/val/test from prepare_subset.py; refusing arbitrary data splits.")
    fit = np.isin(splits, ("train", "val")) if args.include_validation else splits == "train"
    fit_signers = set(signers[fit])
    test_signers = set(signers[splits == "test"])
    overlap = fit_signers & test_signers
    if overlap:
        raise SystemExit(f"Signer leakage detected between fit and test ({len(overlap)} signers). Refusing to report evaluation.")
    x = batch_temporal_summary(features, masks)
    y = labels
    if len(np.unique(y[fit])) < 2:
        raise SystemExit("At least two real training glosses are required; no model was trained.")
    absent = sorted(set(np.unique(y)) - set(np.unique(y[fit])))
    if absent:
        raise SystemExit(f"Glosses have no training samples: {absent}. Adjust the signer subset; no model was trained.")

    estimator = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=3000, class_weight="balanced", random_state=args.seed),
    )
    estimator.fit(x[fit], y[fit])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(estimator, args.output)

    counts = {name: int((splits == name).sum()) for name in ("train", "val", "test")}
    metadata_path = args.metadata or args.output.with_suffix(".metadata.json")
    metadata = {
        "training_status": "completed",
        "task": "isolated-word ASL gloss classification; not phrases or ASL grammar",
        "model_family": "StandardScaler + LogisticRegression baseline",
        "model_path": str(args.output),
        "input_archive": str(args.features),
        "input_shape": list(features.shape[1:]),
        "feature_schema": FEATURE_SCHEMA,
        "labels": estimator.classes_.tolist(),
        "label_map": {str(index): label for index, label in enumerate(estimator.classes_.tolist())},
        "sample_count": size,
        "signer_count": int(len(set(signers))),
        "sample_count_by_split": counts,
        "signer_independent_assertion": True,
        "fit_splits": ["train", "val"] if args.include_validation else ["train"],
        "fit_sample_count": int(fit.sum()),
        "fit_signer_count": int(len(fit_signers)),
        "validation_included_after_model_selection": bool(args.include_validation),
        "seed": args.seed,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": "Not computed by training; run ai/evaluate.py on held-out split.",
        "limitations": ["This model is a small research baseline and may fail on live-camera/domain variations.", "No phrase, grammar, facial, or validated component assessment."],
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    metadata_path.with_name("label_map.json").write_text(json.dumps(metadata["label_map"], indent=2), encoding="utf-8")
    print(json.dumps({"model": str(args.output), "metadata": str(metadata_path), "samples": counts, "labels": len(estimator.classes_)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
