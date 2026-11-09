"""Plan or range-extract selected ASL Citizen clips; never fetches the full ZIP.

The official Microsoft research license is non-commercial/non-revenue, forbids redistribution,
and requires use to match participant consent. Selected files and manifests are kept under
ignored datasets/raw/ and datasets/processed/. Run the plan first and review its class/count/
byte report before invoking --download. The user's initial 2 GiB cap and 5 GiB hard cap apply.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import zipfile
from collections import defaultdict
from io import TextIOWrapper
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ai.scripts.inspect_asl_citizen_zip import DEFAULT_URL, HttpRangeReader, MAX_RANGE_BUDGET, signer_group  # noqa: E402

DEFAULT_CLASSES = ROOT / "ai/config/asl_citizen_6_class_pilot.json"
DEFAULT_DESTINATION = ROOT / "datasets/raw/asl_citizen"
DEFAULT_PLAN = ROOT / "datasets/processed/asl_citizen_6_class_plan.json"
INITIAL_CAP = 2 * 1024**3
HARD_CAP = 5 * 1024**3
CHUNK_SIZE = 1024 * 1024


def read_plan(reader: HttpRangeReader, class_path: Path, seed: str) -> tuple[dict, list[zipfile.ZipInfo]]:
    class_config = json.loads(class_path.read_text(encoding="utf-8"))
    labels = [str(row["gloss"]).casefold() for row in class_config.get("classes", [])]
    if not labels:
        raise ValueError("Subset config has no selected glosses")
    report: dict[str, dict] = {
        label: {"samples": [], "source_signers": set(), "project_signers": {split: set() for split in ("train", "val", "test")},
                "official_split_rows": {split: 0 for split in ("train", "val", "test")}}
        for label in labels
    }
    with zipfile.ZipFile(reader) as archive:
        entries = archive.infolist()
        video_entries = [
            entry for entry in entries
            if Path(entry.filename).suffix.casefold() in {".mp4", ".mov", ".webm", ".mkv"}
        ]
        files_by_basename: dict[str, list[zipfile.ZipInfo]] = defaultdict(list)
        for entry in video_entries:
            files_by_basename[Path(entry.filename).name.casefold()].append(entry)

        for split in ("train", "val", "test"):
            csv_info = next((item for item in entries if item.filename.casefold().endswith(f"/splits/{split}.csv")), None)
            if csv_info is None:
                raise ValueError(f"Official split CSV missing: {split}")
            with archive.open(csv_info, "r") as raw, TextIOWrapper(raw, encoding="utf-8-sig", newline="") as text:
                for row in csv.DictReader(text):
                    gloss = str(row.get("Gloss", "")).strip().casefold()
                    if gloss not in report:
                        continue
                    participant = str(row.get("Participant ID", "")).strip()
                    video_name = Path(str(row.get("Video file", ""))).name
                    matching = files_by_basename.get(video_name.casefold(), [])
                    if not participant:
                        raise ValueError(f"Selected metadata row lacks participant ID: {gloss}/{video_name}")
                    if len(matching) != 1:
                        raise ValueError(f"Selected video entry missing/ambiguous in ZIP: {gloss}/{video_name} ({len(matching)} matches)")
                    entry = matching[0]
                    report[gloss]["samples"].append({
                        "gloss": gloss,
                        "participant_id": participant,
                        "signer_id": participant,
                        "video_file": video_name,
                        "video_id": Path(video_name).stem,
                        "zip_member": entry.filename,
                        "official_split": split,
                        "project_split": split,
                        "compressed_bytes": entry.compress_size,
                        "uncompressed_bytes": entry.file_size,
                    })
                    report[gloss]["source_signers"].add(participant)
                    report[gloss]["project_signers"][split].add(participant)
                    report[gloss]["official_split_rows"][split] += 1

    all_samples = [sample for gloss in labels for sample in report[gloss]["samples"]]
    if not all_samples:
        raise ValueError("None of the selected glosses exist in the official split metadata")
    split_signers = {
        split: {sample["participant_id"] for sample in all_samples if sample["project_split"] == split}
        for split in ("train", "val", "test")
    }
    overlap = {
        f"{left}/{right}": len(split_signers[left] & split_signers[right])
        for left, right in (("train", "val"), ("train", "test"), ("val", "test"))
    }
    if any(overlap.values()):
        raise ValueError(f"Official ASL Citizen participant splits overlap: {overlap}; refusing to claim signer-independent split")

    classes = []
    for gloss in labels:
        stats = report[gloss]
        rows = stats["samples"]
        classes.append({
            "gloss": gloss,
            "video_count": len(rows),
            "participant_count": len(stats["source_signers"]),
            "videos_by_split": stats["official_split_rows"],
            "participants_by_split": {split: len(stats["project_signers"][split]) for split in ("train", "val", "test")},
            "compressed_video_bytes": sum(sample["compressed_bytes"] for sample in rows),
            "uncompressed_video_bytes": sum(sample["uncompressed_bytes"] for sample in rows),
        })
    payload_bytes = sum(sample["compressed_bytes"] for sample in all_samples)
    range_index_bytes = reader.bytes_read
    # ZIP local header/filename/extra fields add a small amount beyond compressed payload.
    overhead_estimate = sum(128 + len(sample["zip_member"].encode("utf-8")) for sample in all_samples)
    plan = {
        "schema_version": "asl-citizen-range-subset-v1",
        "source": "Microsoft Research ASL Citizen; official range-enabled archive",
        "license": "Non-commercial/non-revenue research only; no redistribution; preserve participant-consent limits.",
        "archive_total_bytes": reader.size,
        "selected_glosses": labels,
        "class_summary": classes,
        "video_count": len(all_samples),
        "unique_participants": len({sample["participant_id"] for sample in all_samples}),
        "official_split_participant_overlap": overlap,
        "split_policy": "Use official train/val/test split; verified no participant overlap in selected metadata.",
        "zip_index_and_split_metadata_range_bytes": range_index_bytes,
        "selected_compressed_video_payload_bytes": payload_bytes,
        "estimated_extra_zip_headers_bytes": overhead_estimate,
        "estimated_total_range_transfer_bytes": range_index_bytes + payload_bytes + overhead_estimate,
        "download_ceiling_bytes": INITIAL_CAP,
        "download_performed": False,
        "video_samples": all_samples,
    }
    return plan, video_entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classes", type=Path, default=DEFAULT_CLASSES)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--plan-output", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--max-total-bytes", type=int, default=INITIAL_CAP, help="Initial default 2 GiB; hard maximum 5 GiB")
    parser.add_argument("--download", action="store_true", help="Range-extract only planned videos; no full ZIP download")
    parser.add_argument("--accept-plan", action="store_true", help="Confirm the displayed selected-class plan and non-redistribution conditions")
    args = parser.parse_args()
    if not args.classes.is_file():
        parser.error(f"Class selection missing: {args.classes}")
    if not 0 < args.max_total_bytes <= HARD_CAP:
        parser.error("--max-total-bytes must be greater than zero and no more than the 5 GiB hard cap")

    import urllib.request
    from urllib.error import URLError

    head = urllib.request.Request(args.url, method="HEAD", headers={"User-Agent": "SIGNTALK-research-subset/1.0"})
    try:
        with urllib.request.urlopen(head, timeout=30) as response:
            size = int(response.headers.get("Content-Length") or 0)
            if response.status != 200 or "bytes" not in response.headers.get("Accept-Ranges", "").casefold():
                raise SystemExit("The official source no longer supports HTTP Range; no archive data was downloaded.")
            etag = response.headers.get("ETag")
    except URLError as exc:
        raise SystemExit(f"Cannot access official ASL Citizen archive metadata: {exc}; no archive data downloaded.") from exc
    if not size:
        raise SystemExit("Official archive size unknown; refusing to inspect or download.")

    range_reader = HttpRangeReader(args.url, size, etag, args.max_total_bytes)
    plan, video_entries = read_plan(range_reader, args.classes, seed="asl-citizen")
    plan["destination"] = str(args.destination)
    plan["download_ceiling_bytes"] = args.max_total_bytes
    plan["metadata_only_range_bytes_fetched"] = range_reader.bytes_read
    args.plan_output.parent.mkdir(parents=True, exist_ok=True)
    # Keep participant IDs and clip mappings in ignored local workspace only.
    args.plan_output.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    summary = {key: value for key, value in plan.items() if key != "video_samples"}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Subset plan saved locally (contains participant IDs; do not share): {args.plan_output}")

    if not args.download:
        print("PLAN ONLY: the archive index/split CSVs were range-read; no video member downloaded.")
        return 0
    if not args.accept_plan:
        raise SystemExit("No videos downloaded. Review the plan, then rerun --download --accept-plan if authorized.")
    estimate = int(plan["estimated_total_range_transfer_bytes"])
    if estimate > args.max_total_bytes:
        raise SystemExit(f"Plan estimate {estimate} bytes exceeds the selected byte cap {args.max_total_bytes}; no video downloaded.")

    sample_by_member = {sample["zip_member"]: sample for sample in plan["video_samples"]}
    info_by_name = {entry.filename: entry for entry in video_entries}
    video_root = args.destination / "videos"
    video_root.mkdir(parents=True, exist_ok=True)
    written = 0
    with zipfile.ZipFile(range_reader) as archive:
        for member, sample in sample_by_member.items():
            target = video_root / sample["video_file"]
            if target.exists():
                if target.stat().st_size == sample["uncompressed_bytes"]:
                    print(f"already exists: {sample['gloss']} / {sample['video_id']}")
                    continue
                raise FileExistsError(f"Refusing to overwrite non-matching file: {target}")
            info = info_by_name[member]
            temporary = target.with_suffix(target.suffix + ".part")
            received = 0
            try:
                with archive.open(info, "r") as input_file, temporary.open("xb") as output_file:
                    while chunk := input_file.read(1024 * 1024):
                        received += len(chunk)
                        if range_reader.bytes_read > args.max_total_bytes:
                            raise RuntimeError("HTTP range transfer exceeded the approved byte cap")
                        output_file.write(chunk)
                if received != sample["uncompressed_bytes"]:
                    raise RuntimeError(f"Extracted file size mismatch for {member}")
                temporary.replace(target)
                written += 1
                print(f"extracted {sample['gloss']} / {sample['video_id']} ({received} bytes)")
            except Exception:
                temporary.unlink(missing_ok=True)
                raise
    final_manifest = args.destination / "subset_manifest.json"
    final_manifest.parent.mkdir(parents=True, exist_ok=True)
    final_manifest.write_text(json.dumps({**plan, "download_performed": True, "videos_written": written,
                                           "range_bytes_transferred": range_reader.bytes_read}, indent=2), encoding="utf-8")
    print(f"Range-extracted {written} selected videos only. Local manifest: {final_manifest}")
    print("No full ASL Citizen archive was downloaded; keep all clips/manifests private under the license.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
