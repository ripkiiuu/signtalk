"""Guarded downloader for explicitly approved direct-file WLASL subset URLs.

Default is a local metadata-only dry run. It never invokes yt-dlp and always skips YouTube URLs.
To probe source sizes or download direct files, the user must first review terms, pass
--rights-confirmed, and explicitly allow every source hostname. Download requires an explicit
byte budget no larger than the user's 5 GiB total limit (start with <=2 GiB).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "datasets/WLASL/start_kit/WLASL_v0.3.json"
DEFAULT_CLASSES = ROOT / "ai/config/wlasl_8_classes.json"
DEFAULT_DESTINATION = ROOT / "datasets/raw/wlasl/videos"
DEFAULT_SIZE_PLAN = ROOT / "datasets/processed/wlasl_size_probe.json"
MAX_BUDGET = 5 * 1024**3
CHUNK_SIZE = 1024 * 1024


def select_samples(manifest: list[dict], labels: list[str]) -> list[dict]:
    by_gloss = {str(row.get("gloss", "")).casefold(): row for row in manifest}
    output: list[dict] = []
    missing = []
    for label in labels:
        row = by_gloss.get(label.casefold())
        if row is None:
            missing.append(label)
            continue
        for item in row.get("instances", []):
            url = str(item.get("url", ""))
            host = (urlparse(url).hostname or "").casefold()
            output.append({"gloss": row["gloss"], "video_id": str(item.get("video_id", "")), "signer_id": item.get("signer_id"), "url": url, "host": host})
    if missing:
        raise ValueError(f"Selected classes absent from manifest: {missing}")
    return output


def head_size(sample: dict, allowed_hosts: set[str]) -> tuple[int | None, str]:
    host = sample["host"]
    if host not in allowed_hosts:
        return None, "host_not_allowlisted"
    parsed = urlparse(sample["url"])
    if parsed.scheme != "https" or "youtube.com" in host or "youtu.be" in host:
        return None, "not_an_allowlisted_direct_https_video"
    request = urllib.request.Request(sample["url"], method="HEAD", headers={"User-Agent": "SIGNTALK-research-prototype/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            final_host = (urlparse(response.geturl()).hostname or "").casefold()
            if final_host not in allowed_hosts:
                return None, "redirected_outside_allowlist"
            content_type = response.headers.get_content_type()
            if content_type not in {"video/mp4", "application/mp4"}:
                return None, f"not_mp4_content_type:{content_type}"
            value = response.headers.get("Content-Length")
            return (int(value), "estimated_from_content_length") if value else (None, "content_length_missing")
    except (OSError, urllib.error.URLError, ValueError) as exc:
        return None, f"head_failed:{type(exc).__name__}"


def download_one(sample: dict, allowed_hosts: set[str], destination: Path, remaining: int) -> tuple[int, str]:
    host = sample["host"]
    parsed = urlparse(sample["url"])
    if host not in allowed_hosts or parsed.scheme != "https" or "youtube.com" in host or "youtu.be" in host:
        raise ValueError("Only allowlisted, direct HTTPS files may be downloaded; YouTube URLs are never scraped.")
    request = urllib.request.Request(sample["url"], headers={"User-Agent": "SIGNTALK-research-prototype/1.0"})
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / f"{sample['video_id']}.mp4"
    if target.exists():
        return 0, "already_exists"
    temporary = target.with_suffix(target.suffix + ".part")
    received = 0
    try:
        with urllib.request.urlopen(request, timeout=30) as response, temporary.open("wb") as output:
            final_host = (urlparse(response.geturl()).hostname or "").casefold()
            content_type = response.headers.get_content_type()
            if final_host not in allowed_hosts or content_type not in {"video/mp4", "application/mp4"}:
                raise ValueError("Response redirected outside allowlist or was not an MP4 content type.")
            declared = response.headers.get("Content-Length")
            if not declared:
                raise ValueError("No Content-Length; refusing an unbounded video download.")
            if int(declared) > remaining:
                raise ValueError("Declared size exceeds the remaining user-approved byte budget.")
            while block := response.read(CHUNK_SIZE):
                received += len(block)
                if received > remaining:
                    raise ValueError("Streaming response exceeded the user-approved byte budget.")
                output.write(block)
        temporary.replace(target)
        return received, "downloaded"
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def plan_fingerprint(samples: list[dict], allowed_hosts: set[str]) -> str:
    selected = [
        (sample["gloss"], sample["video_id"], sample["url"], sample["host"])
        for sample in samples
        if sample["host"] in allowed_hosts and "youtube.com" not in sample["host"] and "youtu.be" not in sample["host"]
    ]
    content = json.dumps(sorted(selected), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--classes", type=Path, default=DEFAULT_CLASSES)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--allow-host", action="append", default=[], help="Exact authorized HTTPS hostname; repeat per host")
    parser.add_argument("--rights-confirmed", action="store_true", help="Confirm supervisor/source terms were reviewed for computational use")
    parser.add_argument("--probe-sizes", action="store_true", help="Issue HEAD requests to allowlisted direct video hosts; no video body is downloaded")
    parser.add_argument("--download", action="store_true", help="Download only allowlisted direct files after a size probe")
    parser.add_argument("--max-total-bytes", type=int, help="Mandatory download cap (max 5 GiB; use <=2 GiB for the first pass)")
    parser.add_argument("--probe-output", type=Path, default=DEFAULT_SIZE_PLAN, help="Where --probe-sizes saves its reviewable estimate")
    parser.add_argument("--size-plan", type=Path, help="Previously reviewed JSON created by --probe-sizes; required by --download")
    args = parser.parse_args()
    if not args.manifest.is_file() or not args.classes.is_file():
        parser.error("Manifest or class config is missing")
    class_config = json.loads(args.classes.read_text(encoding="utf-8"))
    labels = [str(item["gloss"]) for item in class_config.get("classes", [])]
    samples = select_samples(json.loads(args.manifest.read_text(encoding="utf-8")), labels)
    allowed = {host.casefold() for host in args.allow_host}
    if args.probe_sizes and args.download:
        parser.error("Use two steps: run --probe-sizes, review its saved report, then run --download --size-plan.")
    if (args.probe_sizes or args.download) and not args.rights_confirmed:
        parser.error("Review C-UDA/upstream rights and PKM terms first; pass --rights-confirmed only after that review.")
    if args.download:
        if not args.max_total_bytes or not (0 < args.max_total_bytes <= MAX_BUDGET):
            parser.error("--download requires --max-total-bytes between 1 byte and 5 GiB")
        if not allowed:
            parser.error("--download requires at least one exact --allow-host reviewed for these clips")
        if not args.size_plan or not args.size_plan.is_file():
            parser.error("--download requires a previously reviewed --size-plan from --probe-sizes")
    if args.probe_sizes and not allowed:
        parser.error("--probe-sizes requires one or more reviewed --allow-host values")

    per_class = []
    unique_video_ids: set[str] = set()
    unique_signer_ids: set[str] = set()
    for label in labels:
        rows = [sample for sample in samples if sample["gloss"].casefold() == label.casefold()]
        local = sum((args.destination / f"{sample['video_id']}.mp4").is_file() for sample in rows)
        unique_video_ids.update(sample["video_id"] for sample in rows if sample["video_id"])
        unique_signer_ids.update(str(sample["signer_id"]) for sample in rows if sample.get("signer_id") is not None)
        youtube_count = sum("youtube.com" in sample["host"] or "youtu.be" in sample["host"] for sample in rows)
        per_class.append({"gloss": label, "manifest_instances": len(rows), "local_clips_present": local,
                          "distinct_signers_in_metadata": len({str(sample["signer_id"]) for sample in rows if sample.get("signer_id") is not None}),
                          "youtube_metadata_urls_not_authorized_for_download": youtube_count,
                          "non_youtube_metadata_urls_not_yet_rights_checked": len(rows) - youtube_count,
                          "other_source_hosts_unverified": sorted({sample["host"] for sample in rows if sample["host"] and "youtube.com" not in sample["host"] and "youtu.be" not in sample["host"]})})
    print(json.dumps({"classes": per_class, "destination": str(args.destination), "downloaded": 0,
                      "total_metadata_instances": len(samples), "unique_video_ids_in_metadata": len(unique_video_ids),
                      "distinct_signers_in_metadata": len(unique_signer_ids),
                      "estimated_total_bytes": None, "estimate_note": "No size exists in WLASL metadata. Use --probe-sizes with reviewed --allow-host values to obtain source Content-Length. No network request is made in default plan mode.",
                      "youtube_urls": "always skipped; no yt-dlp/scraping in this utility", "rights_confirmed": args.rights_confirmed}, indent=2, ensure_ascii=False))

    if not args.probe_sizes and not args.download:
        print("PLAN ONLY: no network request and no download performed.")
        return 0
    candidates = [sample for sample in samples if sample["host"] in allowed and "youtube.com" not in sample["host"] and "youtu.be" not in sample["host"]]
    estimates = [(sample, *head_size(sample, allowed)) for sample in candidates]
    sized = [(sample, size) for sample, size, status in estimates if size is not None and status == "estimated_from_content_length"]
    unknown = [sample for sample, size, status in estimates if size is None]
    total_size = sum(size for _, size in sized)
    estimate_by_class: dict[str, int] = {}
    known_count_by_class: dict[str, int] = {}
    unknown_count_by_class: dict[str, int] = {}
    for sample, size, _ in estimates:
        label = sample["gloss"]
        if size is None:
            unknown_count_by_class[label] = unknown_count_by_class.get(label, 0) + 1
        else:
            estimate_by_class[label] = estimate_by_class.get(label, 0) + size
            known_count_by_class[label] = known_count_by_class.get(label, 0) + 1
    class_estimates = [
        {"gloss": label, "allowlisted_candidates": sum(s["gloss"] == label for s in candidates),
         "size_known_count": known_count_by_class.get(label, 0), "size_unknown_count": unknown_count_by_class.get(label, 0),
         "estimated_bytes": estimate_by_class.get(label) if not unknown_count_by_class.get(label) else None}
        for label in labels
    ]
    print(json.dumps({"destination": str(args.destination), "class_size_estimates": class_estimates,
                      "allowed_host_candidates": len(candidates), "size_known_count": len(sized), "size_unknown_count": len(unknown),
                      "estimated_total_bytes": total_size if not unknown else None,
                      "size_status": {status: sum(item[2] == status for item in estimates) for _, _, status in estimates}}, indent=2, ensure_ascii=False))
    if args.probe_sizes and not args.download:
        probe_report = {
            "plan_fingerprint": plan_fingerprint(samples, allowed),
            "allowed_hosts": sorted(allowed),
            "labels": labels,
            "destination": str(args.destination),
            "size_known_count": len(sized),
            "size_unknown_count": len(unknown),
            "estimated_total_bytes": total_size if not unknown else None,
            "class_size_estimates": class_estimates,
            "probe_performed_by_user_command": True,
            "video_downloaded": False,
        }
        args.probe_output.parent.mkdir(parents=True, exist_ok=True)
        args.probe_output.write_text(json.dumps(probe_report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"SIZE PROBE ONLY: no video body downloaded. Review the estimate at {args.probe_output} before a separate --download command.")
        return 0
    if unknown:
        raise SystemExit("Refusing download: some allowlisted candidate sizes are unknown or failed HEAD.")
    if total_size > args.max_total_bytes:
        raise SystemExit(f"Refusing download: estimate {total_size} exceeds byte cap {args.max_total_bytes}.")
    approved_plan = json.loads(args.size_plan.read_text(encoding="utf-8"))
    if approved_plan.get("plan_fingerprint") != plan_fingerprint(samples, allowed):
        raise SystemExit("Refusing download: selected classes/URLs/allowlist differ from the reviewed size plan. Probe again.")
    if approved_plan.get("estimated_total_bytes") != total_size or approved_plan.get("size_unknown_count") != 0:
        raise SystemExit("Refusing download: reviewed size estimate is incomplete or changed. Probe again.")
    print(f"Using reviewed size plan. Destination: {args.destination}; estimate: {total_size} bytes; cap: {args.max_total_bytes} bytes.")
    transferred = 0
    downloaded = 0
    for sample, size in sized:
        received, status = download_one(sample, allowed, args.destination, args.max_total_bytes - transferred)
        transferred += received
        downloaded += status == "downloaded"
        print(f"{status}: {sample['gloss']} / {sample['video_id']} ({received} bytes)")
    print(f"Completed: {downloaded} files / {transferred} bytes. YouTube URLs were skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
