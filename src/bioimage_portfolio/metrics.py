from __future__ import annotations

from collections.abc import Sequence
import numpy as np


def binary_iou(true_mask: np.ndarray, pred_mask: np.ndarray) -> float:
    """Intersection-over-union for foreground/background masks."""
    true_fg = np.asarray(true_mask) > 0
    pred_fg = np.asarray(pred_mask) > 0
    union = np.logical_or(true_fg, pred_fg).sum()
    if union == 0:
        return 1.0
    intersection = np.logical_and(true_fg, pred_fg).sum()
    return float(intersection / union)


def count_error(true_mask: np.ndarray, pred_mask: np.ndarray) -> int:
    """Signed object-count error: predicted count minus true count."""
    true_n = int(np.asarray(true_mask).max())
    pred_n = int(np.asarray(pred_mask).max())
    return pred_n - true_n


def summarize_counts(true_masks: Sequence[np.ndarray], pred_masks: Sequence[np.ndarray]) -> dict[str, float]:
    """Summarise absolute and relative object-count errors."""
    if len(true_masks) != len(pred_masks):
        raise ValueError("true_masks and pred_masks must have the same length")
    true_counts = np.array([int(np.asarray(m).max()) for m in true_masks], dtype=float)
    pred_counts = np.array([int(np.asarray(m).max()) for m in pred_masks], dtype=float)
    abs_error = np.abs(pred_counts - true_counts)
    denom = np.maximum(true_counts, 1.0)
    return {
        "mean_true_count": float(true_counts.mean()) if len(true_counts) else 0.0,
        "mean_pred_count": float(pred_counts.mean()) if len(pred_counts) else 0.0,
        "mean_absolute_error": float(abs_error.mean()) if len(abs_error) else 0.0,
        "mean_absolute_percentage_error": float((abs_error / denom).mean()) if len(abs_error) else 0.0,
    }
