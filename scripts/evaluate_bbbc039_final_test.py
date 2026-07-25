#!/usr/bin/env python
"""
Final locked evaluation of the fine-tuned Cellpose model on the official
BBBC039 test split.

This script:
1. Reads the official 50-image test list.
2. Finds the matching TIFF images and PNG ground-truth masks.
3. Decodes the color masks into connected instance labels.
4. Runs the locked fine-tuned Cellpose model once.
5. Calculates AP@0.50/0.75/0.90, AJI, and nucleus-count errors.
6. Saves predictions, per-image metrics, a summary, and run configuration.

The test results must not be used to alter the model or inference parameters.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import cellpose
import numpy as np
import pandas as pd
import scipy
import tifffile
import torch
from cellpose import metrics, models
from scipy import ndimage
from skimage.io import imread


MODEL_NAME = "bbbc039_cpsam_v2_pilot40_e100"
CELLPROB_THRESHOLD = 0.0
FLOW_THRESHOLD = 0.4
MIN_SIZE = 15
BATCH_SIZE = 8
IOU_THRESHOLDS = [0.50, 0.75, 0.90]


def find_one(root: Path, filename: str) -> Path:
    matches = [
        path
        for path in root.rglob(filename)
        if "__MACOSX" not in path.parts
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one '{filename}' below {root}, "
            f"but found {len(matches)}:\n"
            + "\n".join(str(path) for path in matches)
        )
    return matches[0]


def build_stem_map(root: Path, suffix: str) -> dict[str, Path]:
    paths = [
        path
        for path in root.rglob(f"*{suffix}")
        if "__MACOSX" not in path.parts
    ]

    output: dict[str, Path] = {}
    duplicates: list[str] = []

    for path in paths:
        if path.stem in output:
            duplicates.append(path.stem)
        else:
            output[path.stem] = path

    if duplicates:
        raise RuntimeError(
            "Duplicate filename stems were found:\n"
            + "\n".join(sorted(set(duplicates)))
        )

    return output


def decode_color_mask(mask_path: Path) -> np.ndarray:
    """
    Convert a BBBC039 color PNG into a 2D instance-label image.

    Different disconnected nuclei may reuse the same RGB color, so every
    connected component of every foreground color is assigned a new label.
    """
    color_mask = np.asarray(imread(mask_path))

    if color_mask.ndim == 2:
        # Defensive support for an already-labelled or grayscale PNG.
        foreground = color_mask != 0
        labels, _ = ndimage.label(
            foreground,
            structure=np.ones((3, 3), dtype=np.uint8),
        )
        return labels.astype(np.int32)

    if color_mask.ndim != 3 or color_mask.shape[-1] < 3:
        raise ValueError(
            f"Unexpected mask shape {color_mask.shape} for {mask_path}"
        )

    rgb = color_mask[..., :3]
    flat = rgb.reshape(-1, 3)
    colors, counts = np.unique(flat, axis=0, return_counts=True)

    zero_color = np.array([0, 0, 0], dtype=colors.dtype)
    zero_matches = np.all(colors == zero_color, axis=1)

    if np.any(zero_matches):
        background_color = zero_color
    else:
        # Defensive fallback if a file does not use black for background.
        background_color = colors[np.argmax(counts)]

    labels = np.zeros(rgb.shape[:2], dtype=np.int32)
    next_label = 1
    connectivity = np.ones((3, 3), dtype=np.uint8)

    for color in colors:
        if np.array_equal(color, background_color):
            continue

        binary = np.all(rgb == color, axis=-1)
        components, n_components = ndimage.label(
            binary,
            structure=connectivity,
        )

        for component_id in range(1, n_components + 1):
            labels[components == component_id] = next_label
            next_label += 1

    return labels


def prepare_cellpose_image(image_path: Path) -> np.ndarray:
    """
    Match the validation workflow: place the single Hoechst channel in the
    first channel and set the two unused channels to zero.
    """
    image = np.asarray(tifffile.imread(image_path))

    if image.ndim != 2:
        raise ValueError(
            f"Expected a 2D image, got shape {image.shape}: {image_path}"
        )

    zeros = np.zeros_like(image)
    return np.stack([image, zeros, zeros], axis=-1)


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    data_root = repo_root / "data" / "BBBC039"
    model_path = repo_root / "models" / MODEL_NAME
    output_dir = repo_root / "results" / "final_test"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not data_root.exists():
        raise FileNotFoundError(f"Dataset folder not found: {data_root}")
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA GPU is not available. Activate the cellpose-modern "
            "environment and confirm CUDA=True before running the final test."
        )

    test_list_path = find_one(data_root / "metadata", "test.txt")
    test_entries = [
        line.strip()
        for line in test_list_path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    if len(test_entries) != 50:
        raise RuntimeError(
            f"Expected 50 official test entries, found {len(test_entries)}."
        )

    test_stems = [Path(entry).stem for entry in test_entries]
    if len(set(test_stems)) != 50:
        raise RuntimeError("The official test list contains duplicate stems.")

    image_by_stem = build_stem_map(data_root / "images", ".tif")
    mask_by_stem = build_stem_map(data_root / "masks", ".png")

    missing_images = [
        stem for stem in test_stems if stem not in image_by_stem
    ]
    missing_masks = [
        stem for stem in test_stems if stem not in mask_by_stem
    ]

    if missing_images or missing_masks:
        raise RuntimeError(
            "Missing test files.\n"
            f"Missing images: {missing_images}\n"
            f"Missing masks: {missing_masks}"
        )

    print("=" * 72)
    print("FINAL LOCKED BBBC039 TEST EVALUATION")
    print("=" * 72)
    print(f"Repository: {repo_root}")
    print(f"Official test list: {test_list_path}")
    print(f"Test images: {len(test_stems)}")
    print(f"Model: {model_path}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        "Locked settings: "
        f"cellprob={CELLPROB_THRESHOLD}, "
        f"flow={FLOW_THRESHOLD}, "
        f"min_size={MIN_SIZE}"
    )
    print("Loading images and decoding ground truth...")

    images = [
        prepare_cellpose_image(image_by_stem[stem])
        for stem in test_stems
    ]
    true_masks = [
        decode_color_mask(mask_by_stem[stem])
        for stem in test_stems
    ]

    image_shapes = {image.shape for image in images}
    mask_shapes = {mask.shape for mask in true_masks}

    if len(image_shapes) != 1 or len(mask_shapes) != 1:
        raise RuntimeError(
            f"Inconsistent shapes: images={image_shapes}, masks={mask_shapes}"
        )

    for stem, image, true_mask in zip(test_stems, images, true_masks):
        if image.shape[:2] != true_mask.shape:
            raise RuntimeError(
                f"Shape mismatch for {stem}: "
                f"image={image.shape}, mask={true_mask.shape}"
            )

    true_counts = np.asarray(
        [int(mask.max()) for mask in true_masks],
        dtype=np.int32,
    )
    nonempty_indices = np.flatnonzero(true_counts > 0)
    empty_indices = np.flatnonzero(true_counts == 0)

    print(
        f"Ground truth: {len(nonempty_indices)} non-empty, "
        f"{len(empty_indices)} empty images"
    )
    print("Loading the fine-tuned model...")

    device = torch.device("cuda:0")
    model = models.CellposeModel(
        device=device,
        pretrained_model=str(model_path),
    )

    print("Running the locked model on the official test split...")
    start = time.perf_counter()

    evaluation_output = model.eval(
        images,
        batch_size=BATCH_SIZE,
        channel_axis=-1,
        normalize=True,
        cellprob_threshold=CELLPROB_THRESHOLD,
        flow_threshold=FLOW_THRESHOLD,
        min_size=MIN_SIZE,
    )

    elapsed_seconds = time.perf_counter() - start
    predicted_masks = [
        np.asarray(mask, dtype=np.int32)
        for mask in evaluation_output[0]
    ]

    if len(predicted_masks) != 50:
        raise RuntimeError(
            f"Expected 50 predicted masks, found {len(predicted_masks)}."
        )

    predicted_counts = np.asarray(
        [int(mask.max()) for mask in predicted_masks],
        dtype=np.int32,
    )

    # Match the validation protocol: overlap metrics are calculated on
    # non-empty ground-truth images; empty images are reported separately.
    true_nonempty = [true_masks[i] for i in nonempty_indices]
    pred_nonempty = [predicted_masks[i] for i in nonempty_indices]

    ap, tp, fp, fn = metrics.average_precision(
        true_nonempty,
        pred_nonempty,
        threshold=IOU_THRESHOLDS,
    )
    aji = metrics.aggregated_jaccard_index(
        true_nonempty,
        pred_nonempty,
    )

    count_error = predicted_counts - true_counts
    absolute_count_error = np.abs(count_error)
    percentage_count_error = np.full(
        len(test_stems),
        np.nan,
        dtype=np.float64,
    )
    percentage_count_error[nonempty_indices] = (
        absolute_count_error[nonempty_indices]
        / true_counts[nonempty_indices]
        * 100.0
    )

    per_image_rows: list[dict[str, object]] = []
    nonempty_position = {
        image_index: position
        for position, image_index in enumerate(nonempty_indices)
    }

    for image_index, stem in enumerate(test_stems):
        row: dict[str, object] = {
            "stem": stem,
            "image_file": image_by_stem[stem].name,
            "ground_truth_file": mask_by_stem[stem].name,
            "ground_truth_count": int(true_counts[image_index]),
            "predicted_count": int(predicted_counts[image_index]),
            "count_error": int(count_error[image_index]),
            "absolute_count_error": int(
                absolute_count_error[image_index]
            ),
            "absolute_percentage_count_error": (
                float(percentage_count_error[image_index])
                if np.isfinite(percentage_count_error[image_index])
                else np.nan
            ),
            "is_empty_ground_truth": bool(
                true_counts[image_index] == 0
            ),
        }

        if image_index in nonempty_position:
            pos = nonempty_position[image_index]
            row.update(
                {
                    "AP@0.50": float(ap[pos, 0]),
                    "AP@0.75": float(ap[pos, 1]),
                    "AP@0.90": float(ap[pos, 2]),
                    "AJI": float(aji[pos]),
                    "TP@0.50": int(tp[pos, 0]),
                    "FP@0.50": int(fp[pos, 0]),
                    "FN@0.50": int(fn[pos, 0]),
                    "TP@0.75": int(tp[pos, 1]),
                    "FP@0.75": int(fp[pos, 1]),
                    "FN@0.75": int(fn[pos, 1]),
                    "TP@0.90": int(tp[pos, 2]),
                    "FP@0.90": int(fp[pos, 2]),
                    "FN@0.90": int(fn[pos, 2]),
                }
            )
        else:
            row.update(
                {
                    "AP@0.50": np.nan,
                    "AP@0.75": np.nan,
                    "AP@0.90": np.nan,
                    "AJI": np.nan,
                    "TP@0.50": np.nan,
                    "FP@0.50": np.nan,
                    "FN@0.50": np.nan,
                    "TP@0.75": np.nan,
                    "FP@0.75": np.nan,
                    "FN@0.75": np.nan,
                    "TP@0.90": np.nan,
                    "FP@0.90": np.nan,
                    "FN@0.90": np.nan,
                }
            )

        per_image_rows.append(row)

    empty_false_positive_objects = int(
        predicted_counts[empty_indices].sum()
    )

    summary = {
        "dataset": "BBBC039v1",
        "split": "official_test",
        "model_name": MODEL_NAME,
        "cellprob_threshold": CELLPROB_THRESHOLD,
        "flow_threshold": FLOW_THRESHOLD,
        "min_size": MIN_SIZE,
        "batch_size": BATCH_SIZE,
        "n_test_images": len(test_stems),
        "n_nonempty_test_images": int(len(nonempty_indices)),
        "n_empty_test_images": int(len(empty_indices)),
        "AP@0.50": float(np.mean(ap[:, 0])),
        "AP@0.75": float(np.mean(ap[:, 1])),
        "AP@0.90": float(np.mean(ap[:, 2])),
        "AJI": float(np.mean(aji)),
        "mean_count_error": float(np.mean(count_error[nonempty_indices])),
        "mean_absolute_count_error": float(
            np.mean(absolute_count_error[nonempty_indices])
        ),
        "mean_absolute_percentage_count_error": float(
            np.mean(percentage_count_error[nonempty_indices])
        ),
        "false_positive_objects_empty": empty_false_positive_objects,
        "evaluation_seconds": float(elapsed_seconds),
        "seconds_per_image": float(elapsed_seconds / len(test_stems)),
        "gpu": torch.cuda.get_device_name(0),
        "python_version": platform.python_version(),
        "cellpose_version": getattr(
            cellpose,
            "__version__",
            "unknown",
        ),
        "pytorch_version": torch.__version__,
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "model_sha256": sha256_file(model_path),
    }

    per_image_df = pd.DataFrame(per_image_rows)
    summary_df = pd.DataFrame([summary])

    per_image_path = output_dir / "final_test_per_image.csv"
    summary_path = output_dir / "final_test_summary.csv"
    predictions_path = output_dir / "final_test_predictions.npz"
    config_path = output_dir / "final_test_run_config.json"
    worst_path = output_dir / "final_test_worst_images.csv"
    stems_path = output_dir / "official_test_stems.txt"

    per_image_df.to_csv(per_image_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    np.savez_compressed(
        predictions_path,
        stems=np.asarray(test_stems),
        masks=np.stack(predicted_masks).astype(np.int32),
    )
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    per_image_df.sort_values(
        ["AP@0.50", "AJI"],
        ascending=[True, True],
        na_position="last",
    ).head(10).to_csv(worst_path, index=False)
    stems_path.write_text(
        "\n".join(test_stems) + "\n",
        encoding="utf-8",
    )

    print("\n" + "=" * 72)
    print("FINAL TEST RESULTS")
    print("=" * 72)
    print(f"AP@0.50: {summary['AP@0.50']:.6f}")
    print(f"AP@0.75: {summary['AP@0.75']:.6f}")
    print(f"AP@0.90: {summary['AP@0.90']:.6f}")
    print(f"AJI:     {summary['AJI']:.6f}")
    print(
        "Mean absolute count error: "
        f"{summary['mean_absolute_count_error']:.4f}"
    )
    print(
        "Mean absolute percentage count error: "
        f"{summary['mean_absolute_percentage_count_error']:.4f}%"
    )
    print(
        "False-positive objects in empty test images: "
        f"{summary['false_positive_objects_empty']}"
    )
    print(
        f"Evaluation time: {elapsed_seconds:.1f} seconds "
        f"({summary['seconds_per_image']:.2f} seconds/image)"
    )
    print("\nSaved:")
    for path in [
        summary_path,
        per_image_path,
        predictions_path,
        config_path,
        worst_path,
        stems_path,
    ]:
        print(f"  {path}")
    print("\nThe test results are final and must not be used to retune the model.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nERROR:", exc, file=sys.stderr)
        raise
