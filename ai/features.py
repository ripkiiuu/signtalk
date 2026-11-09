"""Versioned temporal-summary baseline features for normalized hand landmarks.

Input coordinates are MediaPipe normalized image coordinates (not body-relative).
This simple representation is a classifier baseline, not an ASL component rubric.
"""
from __future__ import annotations

import numpy as np

FEATURE_SCHEMA = "normalized-hand-temporal-summary-v1"


def temporal_summary(sequence: np.ndarray, hand_mask: np.ndarray) -> np.ndarray:
    """Convert (T,2,21,3) coordinates + (T,2) mask to a fixed vector."""
    sequence = np.asarray(sequence, dtype=np.float32)
    hand_mask = np.asarray(hand_mask, dtype=bool)
    if sequence.ndim != 4 or sequence.shape[1:] != (2, 21, 3):
        raise ValueError(f"Expected one sequence shaped (T,2,21,3), got {sequence.shape}")
    if hand_mask.shape != sequence.shape[:2]:
        raise ValueError(f"Hand mask shape {hand_mask.shape} does not match {sequence.shape[:2]}")

    result: list[float] = []
    for hand_slot in range(2):
        valid = np.flatnonzero(hand_mask[:, hand_slot])
        result.append(float(len(valid) / max(1, len(hand_mask))))
        if not len(valid):
            result.extend([0.0] * (21 * 3 * 7))
            continue
        points = sequence[valid, hand_slot]
        # First-to-last deltas and velocity summaries preserve simple temporal evidence.
        deltas = np.diff(points, axis=0)
        summaries = [
            points.mean(axis=0),
            points.std(axis=0),
            points[0],
            points[-1],
            points.min(axis=0),
            points.max(axis=0),
            np.abs(deltas).mean(axis=0) if len(deltas) else np.zeros((21, 3), dtype=np.float32),
        ]
        result.extend(np.stack(summaries, axis=0).transpose(1, 2, 0).reshape(-1).tolist())
    return np.asarray(result, dtype=np.float32)


def batch_temporal_summary(features: np.ndarray, hand_mask: np.ndarray) -> np.ndarray:
    features = np.asarray(features)
    hand_mask = np.asarray(hand_mask)
    if features.ndim != 5 or features.shape[2:] != (2, 21, 3):
        raise ValueError(f"Expected batch shaped (N,T,2,21,3), got {features.shape}")
    if hand_mask.shape != features.shape[:3]:
        raise ValueError(f"Hand mask shape {hand_mask.shape} does not match {features.shape[:3]}")
    return np.stack([temporal_summary(x, m) for x, m in zip(features, hand_mask)], axis=0)
