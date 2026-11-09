"""Extract local MediaPipe hand landmarks from already-authorized WLASL clips.

This command only reads files present under --video-root. It does not fetch URLs.
Expected input clips are preprocessed, one instance per <video_id>.mp4.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="Output from prepare_subset.py")
    parser.add_argument("--video-root", type=Path, required=True, help="Directory containing local <video_id>.mp4 clips")
    parser.add_argument("--output", type=Path, required=True, help="NPZ feature output (keep under ignored datasets/processed/)")
    parser.add_argument("--hand-model", type=Path, default=ROOT / "public/mediapipe/hand_landmarker.task")
    parser.add_argument("--num-frames", type=int, default=32)
    parser.add_argument("--limit", type=int, default=0, help="Optional max clips for a smoke test; 0 means all")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.num_frames < 4:
        raise SystemExit("--num-frames must be at least 4")
    if not args.manifest.is_file():
        raise SystemExit(f"Subset manifest not found: {args.manifest}")
    if not args.video_root.is_dir():
        raise SystemExit(
            f"Local video directory not found: {args.video_root}. No videos are downloaded by this script. "
            "Acquire an authorized subset first and place preprocessed clips there."
        )
    if not args.hand_model.is_file():
        raise SystemExit(f"MediaPipe hand model not found: {args.hand_model}")
    try:
        import cv2
        import mediapipe as mp
        import numpy as np
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
    except ImportError as exc:
        raise SystemExit(
            f"Missing optional CV dependency: {exc}. Install with `python -m pip install -r ai/requirements.txt`."
        ) from exc

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    samples = manifest.get("samples") or manifest.get("video_samples")
    if not isinstance(samples, list) or not samples:
        raise SystemExit("Subset manifest has no samples; rerun prepare_subset.py")
    if args.limit:
        samples = samples[: args.limit]

    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(args.hand_model)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.35,
        min_hand_presence_confidence=0.35,
        min_tracking_confidence=0.35,
    )
    feature_rows: list = []
    mask_rows: list = []
    labels: list[str] = []
    signers: list[str] = []
    splits: list[str] = []
    video_ids: list[str] = []
    skipped: list[dict[str, str]] = []
    global_timestamp_ms = 0

    with vision.HandLandmarker.create_from_options(options) as detector:
        for sample_number, sample in enumerate(samples, start=1):
            video_id = str(sample.get("video_id", ""))
            clip = args.video_root / f"{video_id}.mp4"
            if not clip.is_file():
                skipped.append({"video_id": video_id, "reason": "local_clip_missing"})
                continue
            capture = cv2.VideoCapture(str(clip))
            if not capture.isOpened():
                skipped.append({"video_id": video_id, "reason": "opencv_cannot_open_clip"})
                capture.release()
                continue
            frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = float(capture.get(cv2.CAP_PROP_FPS) or 25.0)
            if frame_count < 1:
                skipped.append({"video_id": video_id, "reason": "empty_clip"})
                capture.release()
                continue

            indices = np.unique(np.linspace(0, frame_count - 1, min(args.num_frames, frame_count), dtype=int))
            sequence = np.zeros((args.num_frames, 2, 21, 3), dtype=np.float32)
            hand_mask = np.zeros((args.num_frames, 2), dtype=np.uint8)
            detected_frames = 0
            frame_slot = 0
            clip_timestamp_base = global_timestamp_ms + 1000
            for frame_index in indices:
                capture.set(cv2.CAP_PROP_POS_FRAMES, int(frame_index))
                ok, bgr = capture.read()
                if not ok or bgr is None:
                    continue
                height, width = bgr.shape[:2]
                if max(height, width) > 640:
                    scale = 640 / max(height, width)
                    bgr = cv2.resize(bgr, (round(width * scale), round(height * scale)))
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                # VIDEO mode requires strictly increasing timestamps across the lifetime
                # of this task; add a gap between clips so tracking state doesn't bridge signers.
                timestamp = clip_timestamp_base + round(int(frame_index) * 1000 / max(fps, 1))
                if timestamp <= global_timestamp_ms:
                    timestamp = global_timestamp_ms + 1
                global_timestamp_ms = timestamp
                result = detector.detect_for_video(image, timestamp)
                landmarks = result.hand_landmarks or []
                if landmarks:
                    detected_frames += 1
                # Use screen-x ordering, not MediaPipe's Left/Right label (whose semantics
                # assume mirrored input). Slots are image-left/image-right, not anatomy.
                ordered_hands = sorted(landmarks[:2], key=lambda points: sum(point.x for point in points) / max(1, len(points)))
                for slot, hand_points in enumerate(ordered_hands):
                    sequence[frame_slot, slot] = np.asarray(
                        [[point.x, point.y, point.z] for point in hand_points], dtype=np.float32
                    )
                    hand_mask[frame_slot, slot] = 1
                frame_slot += 1
                if frame_slot >= args.num_frames:
                    break
            capture.release()
            if detected_frames == 0:
                skipped.append({"video_id": video_id, "reason": "no_hand_detected_in_sampled_frames"})
                continue

            feature_rows.append(sequence)
            mask_rows.append(hand_mask)
            labels.append(str(sample["gloss"]))
            signers.append(str(sample["signer_id"]))
            splits.append(str(sample["project_split"]))
            video_ids.append(video_id)
            print(f"[{sample_number}/{len(samples)}] extracted {video_id} ({detected_frames} frames with hand)")

    if not feature_rows:
        raise SystemExit(
            f"No usable local clips produced hand landmarks. Requested {len(samples)}, missing/undetected {len(skipped)}. "
            "This is not a model prediction; check local video paths, quality, and camera framing."
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output,
        features=np.stack(feature_rows),
        hand_mask=np.stack(mask_rows),
        labels=np.asarray(labels, dtype=str),
        signer_ids=np.asarray(signers, dtype=str),
        splits=np.asarray(splits, dtype=str),
        video_ids=np.asarray(video_ids, dtype=str),
    )
    skipped_path = args.output.with_suffix(".skipped.json")
    skipped_path.write_text(json.dumps(skipped, indent=2), encoding="utf-8")
    print(f"Extracted {len(feature_rows)} clips; skipped {len(skipped)}. Features: {args.output}")
    print(f"Skip report: {skipped_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
