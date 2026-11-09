"""Inspect an official ASL Citizen ZIP via HTTP byte ranges, without downloading videos.

Only the ZIP directory and small metadata members are read. A strict transfer ceiling
prevents accidental full-archive downloads. ASL Citizen data remains non-commercial,
non-redistributable research material under its Microsoft Research license.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from collections import Counter
from io import TextIOWrapper

DEFAULT_URL = "https://download.microsoft.com/download/b/8/8/b88c0bae-e6c1-43e1-8726-98cf5af36ca4/ASL_Citizen.zip"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CLASSES = ROOT / "ai/config/wlasl_8_classes.json"
MAX_RANGE_BUDGET = 256 * 1024 * 1024


def signer_group(participant_id: str, seed: str) -> str:
    digest = hashlib.sha256(f"{seed}:{participant_id}".encode("utf-8")).hexdigest()
    bucket = int(digest[:8], 16) % 100
    return "train" if bucket < 60 else "val" if bucket < 80 else "test"


class HttpRangeReader:
    def __init__(self, url: str, total_size: int, etag: str | None, budget: int):
        self.url, self.size, self.etag, self.budget = url, total_size, etag, budget
        self.position = 0
        self.bytes_read = 0

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.position

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:
            position = offset
        elif whence == 1:
            position = self.position + offset
        elif whence == 2:
            position = self.size + offset
        else:
            raise ValueError("invalid seek whence")
        if position < 0:
            raise ValueError("negative ZIP seek")
        self.position = min(position, self.size)
        return self.position

    def read(self, length: int = -1) -> bytes:
        if length == 0 or self.position >= self.size:
            return b""
        if length < 0:
            length = self.size - self.position
        length = min(length, self.size - self.position)
        if self.bytes_read + length > self.budget:
            raise RuntimeError(f"ZIP metadata read would exceed {self.budget} byte range budget; stopping safely")
        start, end = self.position, self.position + length - 1
        headers = {"Range": f"bytes={start}-{end}", "User-Agent": "SIGNTALK-research-metadata-inspector/1.0"}
        if self.etag:
            headers["If-Range"] = self.etag
        request = urllib.request.Request(self.url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 206:
                raise RuntimeError(f"Server ignored HTTP Range (status {response.status}); full archive will not be read")
            content_range = response.headers.get("Content-Range", "")
            match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", content_range)
            if not match or tuple(map(int, match.groups())) != (start, end, self.size):
                raise RuntimeError(f"Unexpected Content-Range: {content_range!r}; stopping safely")
            data = response.read(length + 1)
        if len(data) != length:
            raise RuntimeError(f"Short range response ({len(data)} of {length} bytes); stopping safely")
        self.position += length
        self.bytes_read += length
        return data

    def close(self) -> None:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--classes", type=Path, default=DEFAULT_CLASSES, help="Glosses to count from the provided subset config")
    parser.add_argument("--seed", default="signtalk-asl-citizen-v1")
    parser.add_argument("--max-range-bytes", type=int, default=MAX_RANGE_BUDGET)
    args = parser.parse_args()
    if not 1 <= args.max_range_bytes <= MAX_RANGE_BUDGET:
        parser.error("--max-range-bytes must be 1..256 MiB")
    head = urllib.request.Request(args.url, method="HEAD", headers={"User-Agent": "SIGNTALK-research-metadata-inspector/1.0"})
    try:
        with urllib.request.urlopen(head, timeout=30) as response:
            total_size = int(response.headers.get("Content-Length") or 0)
            accept_ranges = response.headers.get("Accept-Ranges", "").casefold()
            etag = response.headers.get("ETag")
        if total_size <= 0 or "bytes" not in accept_ranges:
            raise SystemExit("The official archive does not expose reliable byte ranges; no archive data was downloaded.")
        source = HttpRangeReader(args.url, total_size, etag, args.max_range_bytes)
        selected_classes = json.loads(args.classes.read_text(encoding="utf-8"))
        glosses = [str(item["gloss"]).casefold() for item in selected_classes.get("classes", [])]
        if not glosses:
            raise SystemExit("No selected glosses in --classes configuration")
        with zipfile.ZipFile(source) as archive:
            entries = archive.infolist()
            central_directory_bytes = sum(
                46 + len(entry.filename.encode("utf-8")) + len(entry.extra) + len(entry.comment)
                for entry in entries
            )
            use_info = next((entry for entry in entries if entry.filename.casefold().endswith("/use.txt")), None)
            use_notice = ""
            if use_info is not None:
                with archive.open(use_info, "r") as raw:
                    use_notice = raw.read(32 * 1024).decode("utf-8", errors="replace")
            videos = [entry for entry in entries if Path(entry.filename).suffix.casefold() in {".mp4", ".mov", ".webm", ".mkv"}]
            by_filename: dict[str, list[zipfile.ZipInfo]] = {}
            for entry in videos:
                by_filename.setdefault(Path(entry.filename).name.casefold(), []).append(entry)
            summary = {
                gloss: {"metadata_rows": 0, "participants": set(), "metadata_split_participants": {"train": set(), "val": set(), "test": set()},
                        "project_split_participants": {"train": set(), "val": set(), "test": set()}, "split_rows": {"train": 0, "val": 0, "test": 0},
                        "video_names": set(), "matched_video_entries": set(), "unmatched_video_names": 0}
                for gloss in glosses
            }
            for split_name in ("train", "val", "test"):
                info = next((entry for entry in entries if entry.filename.casefold().endswith(f"/splits/{split_name}.csv")), None)
                if info is None:
                    continue
                with archive.open(info, "r") as raw, TextIOWrapper(raw, encoding="utf-8-sig", newline="") as text:
                    reader = csv.DictReader(text)
                    fields = reader.fieldnames
                    for row in reader:
                        gloss = str(row.get("Gloss", "")).strip().casefold()
                        if gloss not in summary:
                            continue
                        participant = str(row.get("Participant ID", "")).strip()
                        video_name = Path(str(row.get("Video file", ""))).name
                        entry_matches = by_filename.get(video_name.casefold(), [])
                        stats = summary[gloss]
                        stats["metadata_rows"] += 1
                        stats["split_rows"][split_name] += 1
                        stats["video_names"].add(video_name)
                        if participant:
                            stats["participants"].add(participant)
                            stats["metadata_split_participants"][split_name].add(participant)
                            stats["project_split_participants"][signer_group(participant, args.seed)].add(participant)
                        if len(entry_matches) == 1:
                            stats["matched_video_entries"].add(entry_matches[0].filename)
                        else:
                            stats["unmatched_video_names"] += 1
            selected_video_entries = {
                name: entry
                for stats in summary.values()
                for name in stats["matched_video_entries"]
                for entry in videos if entry.filename == name
            }
            split_overlap = {}
            split_sets = {split: set().union(*(stats["metadata_split_participants"][split] for stats in summary.values())) for split in ("train", "val", "test")}
            for left, right in (("train", "val"), ("train", "test"), ("val", "test")):
                split_overlap[f"{left}/{right}"] = len(split_sets[left] & split_sets[right])
            class_summary = []
            for gloss in glosses:
                stats = summary[gloss]
                class_summary.append({
                    "gloss": gloss,
                    "metadata_rows": stats["metadata_rows"],
                    "distinct_participants": len(stats["participants"]),
                    "official_split_rows": stats["split_rows"],
                    "project_signer_split_counts": {split: len(stats["project_split_participants"][split]) for split in ("train", "val", "test")},
                    "unique_video_metadata_names": len(stats["video_names"]),
                    "archive_video_matches": len(stats["matched_video_entries"]),
                    "unmatched_or_ambiguous_names": stats["unmatched_video_names"],
                    "selected_compressed_video_bytes": sum(selected_video_entries[name].compress_size for name in stats["matched_video_entries"] if name in selected_video_entries),
                    "selected_uncompressed_video_bytes": sum(selected_video_entries[name].file_size for name in stats["matched_video_entries"] if name in selected_video_entries),
                })
            selected_compressed = sum(entry.compress_size for entry in selected_video_entries.values())
            selected_uncompressed = sum(entry.file_size for entry in selected_video_entries.values())
        metadata = [
            {"name": info.filename, "uncompressed_bytes": info.file_size, "compressed_bytes": info.compress_size}
            for info in entries if Path(info.filename).suffix.casefold() in {".csv", ".tsv", ".json", ".txt", ".yaml", ".yml"}
        ]
        print(json.dumps({
            "source_url": args.url,
            "archive_total_bytes": total_size,
            "server_supports_range": True,
            "range_bytes_fetched": source.bytes_read,
            "zip_entries": len(entries),
            "central_directory_bytes": central_directory_bytes,
            "video_entry_count": len(videos),
            "video_bytes_total_in_archive": sum(info.file_size for info in videos),
            "metadata_candidates": metadata,
            "dataset_use_notice": use_notice,
            "selected_glosses": class_summary,
            "selected_total_metadata_rows": sum(stats["metadata_rows"] for stats in summary.values()),
            "selected_unique_participants": len(set().union(*(stats["participants"] for stats in summary.values()))),
            "source_split_participant_overlap": split_overlap,
            "proposed_60_20_20_signer_split_video_bytes": {
                "compressed_payload": selected_compressed,
                "uncompressed_files": selected_uncompressed,
                "all_selected_classes_have_archive_videos": all(stats["metadata_rows"] > 0 and stats["metadata_rows"] == len(stats["matched_video_entries"]) for stats in summary.values()),
            },
            "note": "Only ZIP central-directory and split-CSV metadata members were range-read. No video member was downloaded or extracted. Bytes are exact ZIP member sizes; HTTP request/header overhead is additional.",
        }, indent=2, ensure_ascii=False))
        return 0
    except urllib.error.URLError as exc:
        raise SystemExit(f"HTTP Range metadata inspection failed; no full archive fallback attempted: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
