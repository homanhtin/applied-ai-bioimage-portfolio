\# Cellpose Baseline Test



\## Environment



\- Date: 24 July 2026

\- Cellpose version: 4.2.1.1

\- Python version: 3.10.20

\- Hardware: CPU

\- Model: cpsam\_v2

\- Input image: 008.tif

\- Detected objects: 16 ROIs



\## Initial observations



The pretrained Cellpose model successfully segmented many round cyst-like

objects without additional training.



Several objects with clear boundaries were detected correctly. Some irregular,

low-contrast, overlapping, or background structures were not segmented or may

require manual review.



The predicted boundaries have not yet been compared with manually annotated

ground-truth masks.



\## Files generated



\- 008.tif

\- 008\_seg.npy



\## Next steps



1\. Preserve this output as the unmodified baseline.

2\. Create manually reviewed ground-truth annotations.

3\. Evaluate object count and boundary accuracy.

4\. Train or fine-tune a custom Cellpose model.

5\. Compare the pretrained and fine-tuned model results.



\## GPU setup



\- GPU: NVIDIA GeForce RTX 3060, 12 GB VRAM

\- NVIDIA driver: 581.42

\- PyTorch version: 2.13.0+cu130

\- CUDA runtime: 13.0

\- CUDA available: True

\- Cellpose GPU status: Enabled



\## GPU test



\- Model: cpsam\_v2

\- Test image: 009.tif

\- Detected objects: 21 ROIs

\- Inference time: approximately 5.29 seconds

\- Result: Cellpose successfully performed segmentation using CUDA with a faster speed, even though the size detection was still not perfect with the undetected large cyst.

