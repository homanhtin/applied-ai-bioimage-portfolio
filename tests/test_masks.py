import numpy as np

from bioimage_portfolio.masks import decode_color_mask, relabel_sequential


def test_decode_rgb_mask():
    mask = np.zeros((4, 5, 3), dtype=np.uint8)
    mask[0:2, 0:2] = [255, 0, 0]
    mask[2:4, 3:5] = [0, 255, 0]
    decoded = decode_color_mask(mask)
    assert decoded.max() == 2
    assert decoded[0, 0] != decoded[3, 4]
    assert decoded[1, 4] == 0


def test_relabel_sequential():
    arr = np.array([[0, 4, 4], [9, 0, 9]])
    out = relabel_sequential(arr)
    assert set(np.unique(out)) == {0, 1, 2}
