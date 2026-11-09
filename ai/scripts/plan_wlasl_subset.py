"""Offline-only WLASL subset plan. It reads metadata but makes no network requests."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "datasets/WLASL/start_kit/WLASL_v0.3.json"
DEFAULT_CLASSES = ROOT / "ai/config/wlasl_8_classes.json"
DEFAULT_DESTINATION = ROOT / "datasets/raw/wlasl/videos"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--classes", type=Path, default=DEFAULT_CLASSES)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    class_config = json.loads(args.classes.read_text(encoding="utf-8"))
    by_gloss = {row["gloss"].casefold(): row for row in manifest}
    report = []
    total = Counter()
    for selected in class_config["classes"]:
        label = str(selected["gloss"])
        row = by_gloss.get(label.casefold())
        if row is None:
            raise SystemExit(f"Selected gloss is missing from WLASL manifest: {label}")
        instances = row.get("instances", [])
        hosts = Counter((urlparse(str(item.get("url", ""))).hostname or "unknown").lower() for item in instances)
        splits = Counter(str(item.get("split", "unknown")) for item in instances)
        youtube = sum(count for host, count in hosts.items() if "youtube.com" in host or "youtu.be" in host)
        report.append({
            "gloss": label,
            "manifest_instances_not_availability": len(instances),
            "distinct_signers": len({str(item.get("signer_id")) for item in instances if item.get("signer_id") is not None}),
            "upstream_split_counts_not_signer_independent": dict(splits),
            "youtube_url_count_not_download_authorization": youtube,
            "host_counts": dict(hosts),
        })
        total["instances"] += len(instances)
        total["youtube_urls"] += youtube

    print(json.dumps({
        "dataset": "WLASL v0.3",
        "class_plan": report,
        "totals": {"classes": len(report), **dict(total)},
        "local_clips_at_destination": sum(1 for path in args.destination.glob("*.mp4")) if args.destination.is_dir() else 0,
        "destination": str(args.destination),
        "estimated_download_bytes": None,
        "size_note": "WLASL JSON has no byte sizes; URLs are mixed-host/YouTube. Estimating requires approved source-specific size probes. No network request was made.",
        "partial_metadata_selection_possible": True,
        "original_upstream_downloader_filters_classes": False,
        "youtube_download_attempts_allowed_by_this_plan": False,
        "download_performed": False,
        "approval_needed": "Verify C-UDA, upstream clip rights, and PKM-KC use before any source requests or downloads.",
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
