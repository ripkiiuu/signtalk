"""Create a small WLASL metadata-only subset with signer-grouped project splits.

This script selects manifest records only. It does not fetch, decode, copy, or download video.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "datasets/WLASL/start_kit/WLASL_v0.3.json"
DEFAULT_CLASS_CONFIG = ROOT / "ai/config/wlasl_8_classes.json"


def signer_split(signer_id: object, seed: str) -> str:
    if signer_id is None:
        raise ValueError("A signer_id is missing; cannot create signer-independent splits safely")
    value = f"{seed}:{signer_id}".encode("utf-8")
    bucket = int(hashlib.sha256(value).hexdigest()[:8], 16) % 100
    if bucket < 60:
        return "train"
    if bucket < 80:
        return "val"
    return "test"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--classes", type=Path, default=DEFAULT_CLASS_CONFIG)
    parser.add_argument("--output", type=Path, required=True, help="Write metadata manifest here; no videos are copied")
    parser.add_argument("--seed", default="signtalk-wlasl-v1", help="Stable split seed")
    parser.add_argument("--max-per-class", type=int, default=0, help="Optional cap (0 means keep all metadata instances)")
    args = parser.parse_args()
    if not args.manifest.is_file():
        parser.error(f"Manifest not found: {args.manifest}")
    if not args.classes.is_file():
        parser.error(f"Class config not found: {args.classes}")
    if args.max_per_class < 0:
        parser.error("--max-per-class must be zero or positive")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    config = json.loads(args.classes.read_text(encoding="utf-8"))
    requested = [str(item["gloss"]).casefold() for item in config.get("classes", [])]
    if not requested:
        parser.error("Class config contains no gloss labels")

    source_by_gloss = {str(row.get("gloss", "")).casefold(): row for row in manifest}
    missing = [label for label in requested if label not in source_by_gloss]
    if missing:
        parser.error(f"Configured labels are not in WLASL manifest: {', '.join(missing)}")

    records: list[dict] = []
    counts_by_class: Counter[str] = Counter()
    for label in requested:
        source = source_by_gloss[label]
        instances = sorted(source.get("instances", []), key=lambda item: str(item.get("video_id", "")))
        if args.max_per_class:
            instances = instances[: args.max_per_class]
        for instance in instances:
            project_split = signer_split(instance.get("signer_id"), args.seed)
            records.append(
                {
                    "gloss": source["gloss"],
                    "video_id": str(instance.get("video_id", "")),
                    "signer_id": str(instance["signer_id"]),
                    "source_url": str(instance.get("url", "")),
                    "source_site": str(instance.get("source", "")),
                    "variation_id": instance.get("variation_id"),
                    "frame_start": instance.get("frame_start"),
                    "frame_end": instance.get("frame_end"),
                    "fps": instance.get("fps", 25),
                    "source_split": instance.get("split"),
                    "project_split": project_split,
                }
            )
            counts_by_class[source["gloss"]] += 1

    split_signers: dict[str, set[str]] = defaultdict(set)
    split_labels: dict[str, set[str]] = defaultdict(set)
    for row in records:
        split_signers[row["project_split"]].add(row["signer_id"])
        split_labels[row["project_split"]].add(row["gloss"])
    for left, right in (("train", "val"), ("train", "test"), ("val", "test")):
        overlap = split_signers[left] & split_signers[right]
        if overlap:
            raise RuntimeError(f"Signer leakage between {left}/{right}: {len(overlap)} signers")
    missing_labels = {split: sorted(set(counts_by_class) - split_labels[split]) for split in ("train", "val", "test")}
    if any(missing_labels.values()):
        raise RuntimeError(
            "At least one class is missing from a signer split. Try another --seed or reduce --max-per-class. "
            f"Missing labels: {missing_labels}"
        )

    output = {
        "schema_version": "signtalk-wlasl-metadata-subset-v1",
        "dataset": "WLASL v0.3",
        "source_manifest": str(args.manifest),
        "license_notice": "C-UDA computational use only; upstream clip rights still require review.",
        "seed": args.seed,
        "split_strategy": "sha256 signer-group split: 60% train / 20% validation / 20% test; same signer never crosses splits",
        "class_counts": dict(sorted(counts_by_class.items())),
        "signer_counts": {split: len(split_signers[split]) for split in ("train", "val", "test")},
        "samples": records,
        "video_downloaded": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: output[key] for key in ("dataset", "class_counts", "signer_counts", "split_strategy", "video_downloaded")}, indent=2, ensure_ascii=False))
    print(f"Metadata-only subset written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
