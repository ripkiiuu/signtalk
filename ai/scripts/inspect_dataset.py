"""Read-only WLASL metadata/video audit. Never downloads or opens a URL."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "datasets/WLASL/start_kit/WLASL_v0.3.json"
DEFAULT_VIDEO_ROOTS = (
    ROOT / "datasets/raw/wlasl/videos",
    ROOT / "datasets/WLASL/start_kit/videos",
    ROOT / "datasets/WLASL/start_kit/raw_videos_mp4",
)
VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".avi"}


def load_manifest(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        rows = json.load(file)
    if not isinstance(rows, list):
        raise ValueError("Expected WLASL v0.3 JSON to contain a top-level list")
    return rows


def audit(rows: list[dict]) -> dict:
    split_signers: dict[str, set[str]] = defaultdict(set)
    split_instances: Counter[str] = Counter()
    sources: Counter[str] = Counter()
    missing_fields: Counter[str] = Counter()
    class_counts: list[tuple[str, int]] = []
    instances = 0

    for entry in rows:
        gloss = str(entry.get("gloss", "")).strip()
        samples = entry.get("instances")
        if not gloss or not isinstance(samples, list):
            missing_fields["class.gloss_or_instances"] += 1
            continue
        class_counts.append((gloss, len(samples)))
        for sample in samples:
            instances += 1
            for field in ("video_id", "url", "signer_id", "split"):
                if sample.get(field) in (None, ""):
                    missing_fields[field] += 1
            split = str(sample.get("split", "unknown"))
            signer = sample.get("signer_id")
            split_instances[split] += 1
            if signer is not None:
                split_signers[split].add(str(signer))
            host = urlparse(str(sample.get("url", ""))).hostname or "unknown"
            sources[host.lower()] += 1

    overlaps: dict[str, int] = {}
    names = sorted(split_signers)
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            overlaps[f"{left}/{right}"] = len(split_signers[left] & split_signers[right])

    return {
        "class_count": len(class_counts),
        "instance_count": instances,
        "classes_with_no_instances": sum(1 for _, count in class_counts if count == 0),
        "split_instance_counts": dict(sorted(split_instances.items())),
        "distinct_signers_by_split": {key: len(value) for key, value in sorted(split_signers.items())},
        "signer_overlap_by_split": overlaps,
        "source_hosts": dict(sources.most_common()),
        "missing_required_fields": dict(missing_fields),
        "top_12_classes": [
            {"gloss": gloss, "instances": count}
            for gloss, count in sorted(class_counts, key=lambda pair: (-pair[1], pair[0].casefold()))[:12]
        ],
    }


def local_video_audit(roots: tuple[Path, ...]) -> dict:
    found: dict[str, int] = {}
    for root in roots:
        if root.is_dir():
            found[str(root)] = sum(
                1 for path in root.rglob("*") if path.is_file() and path.suffix.casefold() in VIDEO_SUFFIXES
            )
        else:
            found[str(root)] = 0
    return {"video_count_by_root": found, "total_local_video_files": sum(found.values())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--video-root", type=Path, action="append", help="Optional local clip root; repeatable")
    args = parser.parse_args()
    if not args.manifest.is_file():
        parser.error(f"Manifest not found: {args.manifest}")

    report = audit(load_manifest(args.manifest))
    roots = tuple(args.video_root) if args.video_root else DEFAULT_VIDEO_ROOTS
    report["manifest_path"] = str(args.manifest)
    report["local_media"] = local_video_audit(roots)
    report["downloaded_anything"] = False
    report["warning"] = (
        "WLASL metadata/source license is not blanket permission for upstream video URLs. "
        "Review C-UDA and video rights before acquiring clips."
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
