"""Export a trained sklearn baseline to ONNX; export is not browser integration by itself."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True, help="Actual joblib artifact from ai/train.py")
    parser.add_argument("--features", type=Path, required=True, help="Same feature archive used to train; used to check input width")
    parser.add_argument("--output", type=Path, default=ROOT / "models/wlasl_hand_baseline.onnx")
    parser.add_argument("--parity-samples", type=int, default=16)
    args = parser.parse_args()
    if not args.model.is_file() or not args.features.is_file():
        raise SystemExit("A real trained model and feature archive are required. No ONNX model exported.")
    try:
        import joblib
        import numpy as np
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType
        import onnx
        from ai.features import batch_temporal_summary
    except ImportError as exc:
        raise SystemExit(f"Missing export dependency: {exc}. Install ai/requirements-export.txt.") from exc

    model = joblib.load(args.model)
    with np.load(args.features, allow_pickle=False) as archive:
        raw = batch_temporal_summary(archive["features"], archive["hand_mask"])
        y = archive["labels"].astype(str)
        splits = archive["splits"].astype(str)
    if not len(raw):
        raise SystemExit("Feature archive is empty; no export performed.")
    feature_width = int(raw.shape[1])
    options = {id(model.steps[-1][1]): {"zipmap": False}}
    graph = convert_sklearn(
        model,
        initial_types=[("features", FloatTensorType([None, feature_width]))],
        options=options,
        target_opset=17,
    )
    model_labels = model.classes_.tolist() if hasattr(model, "classes_") else model[-1].classes_.tolist()
    model_label_map = {str(index): label for index, label in enumerate(model_labels)}
    for key, value in {
        "signtalk.label_map": json.dumps(model_label_map, ensure_ascii=False),
        "signtalk.feature_schema": "normalized-hand-temporal-summary-v1",
        "signtalk.model_scope": "ASL Citizen research subset; isolated-word classes only; non-commercial local research",
    }.items():
        metadata = graph.metadata_props.add()
        metadata.key, metadata.value = key, value
    onnx.checker.check_model(graph)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    onnx.save_model(graph, args.output)
    metadata = {
        "export_status": "onnx_exported",
        "onnx_path": str(args.output),
        "source_model": str(args.model),
        "input_width": feature_width,
        "input_schema": "normalized-hand-temporal-summary-v1",
        "labels": model_labels,
        "label_map": model_label_map,
        "parity": "not checked; install onnxruntime to run parity test",
        "usage_scope": "isolated-word experimental classifier only; no linguistic coaching claim",
    }
    try:
        import onnxruntime as ort

        session = ort.InferenceSession(str(args.output), providers=["CPUExecutionProvider"])
        count = min(max(args.parity_samples, 1), len(raw))
        selected = np.flatnonzero(splits == "test")[:count]
        if not len(selected):
            selected = np.arange(count)
        sklearn_pred = model.predict(raw[selected])
        onnx_values = session.run(None, {session.get_inputs()[0].name: raw[selected].astype(np.float32)})
        onnx_scores = next((value for value in onnx_values if getattr(value, "ndim", 0) == 2), None)
        if onnx_scores is None:
            raise RuntimeError("ONNX graph did not emit a 2D class-score tensor")
        label_order = model.classes_.tolist() if hasattr(model, "classes_") else model[-1].classes_.tolist()
        onnx_pred = np.asarray(label_order)[onnx_scores.argmax(axis=1)]
        parity = bool(np.array_equal(sklearn_pred, onnx_pred))
        metadata["parity"] = {"checked_samples": int(len(selected)), "predicted_labels_match": parity}
        if not parity:
            raise RuntimeError("Python/ONNX labels differ on parity samples; do not integrate this model in the browser.")
    except ImportError:
        pass
    args.output.with_suffix(".metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
