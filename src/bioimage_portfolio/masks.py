from __future__ import annotations

import numpy as np
from skimage.measure import label


def relabel_sequential(mask: np.ndarray) -> np.ndarray:
    """Map non-zero labels to consecutive integers starting at 1."""
    arr = np.asarray(mask)
    out = np.zeros(arr.shape, dtype=np.int32)
    values = np.unique(arr)
    values = values[values != 0]
    for new_label, old_label in enumerate(values, start=1):
        out[arr == old_label] = new_label
    return out


def decode_color_mask(mask: np.ndarray) -> np.ndarray:
    """Decode a BBBC039-style instance mask into a labelled integer array.

    Parameters
    ----------
    mask:
        A 2-D labelled mask, binary mask, or RGB/RGBA image in which each
        object is encoded using a different colour.

    Returns
    -------
    numpy.ndarray
        Integer mask with 0 as background and 1..N as object labels.
    """
    arr = np.asarray(mask)
    if arr.ndim == 2:
        unique = np.unique(arr)
        if set(unique.tolist()).issubset({0, 1, 255}):
            return label(arr > 0, connectivity=1).astype(np.int32)
        return relabel_sequential(arr)

    if arr.ndim != 3 or arr.shape[-1] not in (3, 4):
        raise ValueError(f"Expected a 2-D mask or RGB/RGBA mask, got shape {arr.shape}")

    rgb = arr[..., :3].astype(np.uint32)
    codes = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    out = np.zeros(codes.shape, dtype=np.int32)
    colours = np.unique(codes)
    colours = colours[colours != 0]
    for new_label, colour in enumerate(colours, start=1):
        out[codes == colour] = new_label
    return out
