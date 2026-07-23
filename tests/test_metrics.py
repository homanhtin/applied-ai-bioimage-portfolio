import numpy as np

from bioimage_portfolio.metrics import binary_iou, count_error, summarize_counts


def test_binary_iou_identity():
    mask = np.array([[0, 1], [1, 0]])
    assert binary_iou(mask, mask) == 1.0


def test_count_error():
    true = np.array([[0, 1], [2, 0]])
    pred = np.array([[0, 1], [1, 0]])
    assert count_error(true, pred) == -1


def test_summarize_counts():
    true = [np.array([[0, 1], [2, 0]])]
    pred = [np.array([[0, 1], [1, 0]])]
    summary = summarize_counts(true, pred)
    assert summary["mean_absolute_error"] == 1.0
