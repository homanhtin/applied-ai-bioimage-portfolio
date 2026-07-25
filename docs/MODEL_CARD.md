# Model Card: BBBC039 Cellpose-SAM Pilot Fine-Tuned Model

## Model summary

**Model name:** `bbbc039_cpsam_v2_pilot40_e100`  
**Base model:** Cellpose-SAM `cpsam_v2`  
**Task:** 2D instance segmentation of Hoechst-stained U2OS nuclei  
**Framework:** Cellpose 4.2.1.1 / PyTorch  
**Model format:** Cellpose custom weight file  
**Weight size:** approximately 1.13 GB

This model was fine-tuned as part of a public, reproducible bioimage-analysis portfolio. It is intended to demonstrate validation-driven model development rather than to serve as a universal nucleus-segmentation model.

## Intended use

The model is intended for:

- 2D fluorescence images of U2OS nuclei stained with Hoechst
- images similar in appearance and scale to BBBC039
- research benchmarking and educational demonstration
- reproducible comparison of pretrained and limited-data fine-tuned Cellpose models

The model may also be used as a starting point for evaluation on similar fluorescence nucleus datasets, but transfer to new data must be validated independently.

## Out-of-scope use

The model has not been validated for:

- clinical or diagnostic use
- patient-derived decision-making
- other cell types without independent testing
- brightfield, phase-contrast, or histology images
- whole-cell, cyst, organelle, membrane, or protein segmentation
- 3D stacks
- time-lapse microscopy
- images with substantially different resolution, staining, noise, density, or morphology

## Training data

The model was fine-tuned using 40 deterministically selected images from the official BBBC039 training subset.

Selection was designed to span the observed range of annotated nucleus densities rather than simply using the first 40 files.

The annotations were supplied by the BBBC039 dataset providers. They were not manually created by the repository author.

Two empty training images were excluded from model training. The official validation and test partitions were kept separate.

## Training procedure

- Starting weights: built-in `cpsam_v2`
- Training images: 40
- Validation-monitoring images: 49 non-empty images
- Epochs: 100
- Batch size: 1
- Learning rate: `1e-5`
- Weight decay: `0.1`
- Minimum training masks: 5
- Training block size: 256
- Training hardware: NVIDIA Tesla T4 in Google Colab
- Training time: approximately 72.4 minutes

Validation images were used for monitoring and model selection, not for gradient updates. The official test subset was not opened until the model and inference parameters had been locked.

## Final inference configuration

```yaml
model: bbbc039_cpsam_v2_pilot40_e100
cellprob_threshold: 0.0
flow_threshold: 0.4
min_size: 15
normalize: true
channel_axis: -1
input_representation:
  channel_0: Hoechst image
  channel_1: zeros
  channel_2: zeros
```

## Validation performance

The final balanced configuration achieved approximately:

| Metric | Validation |
|---|---:|
| AP@0.50 | 0.937 |
| AP@0.75 | 0.877 |
| AP@0.90 | 0.641 |
| AJI | 0.940 |
| Mean absolute count error | 3.57 nuclei/image |
| Mean absolute percentage count error | 3.04% |

The empty validation control produced zero false-positive objects.

## Final held-out test performance

The locked model was evaluated once on all 50 images in the official BBBC039 test subset.

| Metric | Test |
|---|---:|
| AP@0.50 | 0.934124 |
| AP@0.75 | 0.871279 |
| AP@0.90 | 0.641172 |
| AJI | 0.936495 |
| Mean absolute count error | 3.6400 nuclei/image |
| Mean absolute percentage count error | 3.2067% |
| Evaluation time | 48.4 seconds |
| Time per image | 0.97 seconds/image |

Test hardware:

- NVIDIA GeForce RTX 3060
- PyTorch CUDA environment
- Cellpose 4.2.1.1

The official test subset contained 50 non-empty images and no empty negative-control images. Therefore, false-positive behavior on empty images was not evaluated on the test set.

These results are final and were not used for further tuning.

## Evaluation metrics

- **AP@0.50, AP@0.75, AP@0.90:** instance-level average precision at increasingly strict IoU thresholds
- **AJI:** aggregated Jaccard index across matched and unmatched instances
- **Mean absolute count error:** average absolute difference between predicted and annotated nucleus counts
- **Mean absolute percentage count error:** count error relative to the annotated count

Overlap metrics were calculated on non-empty ground-truth images. Empty-image false-positive counts were reported separately where an empty control existed.

## Data quality controls

The workflow included:

- verification of 200 image-mask pairs
- validation of the official training, validation, and test splits
- exclusion of `__MACOSX` archive artifacts
- detection of three low-signal empty ground-truth images
- correction of BBBC039 color-mask decoding

A key annotation issue was that disconnected nuclei could reuse the same RGB color. Each disconnected component of every foreground color was therefore assigned a separate instance label.

## Known limitations

- Performance is benchmark-specific.
- Dim, small, irregular, or closely clustered nuclei remain the main failure cases.
- Fine-tuning improved overall balance but did not eliminate under-segmentation.
- AP@0.90 remains lower than AP@0.50 because strict boundary agreement is more difficult.
- The training experiment used only 40 images and one fixed fine-tuning schedule.
- No external dataset was used for validation.
- No uncertainty estimate or calibration analysis was performed.
- The model weight is too large for ordinary GitHub storage and is not committed directly to the repository.

## Reproducibility

Relevant files:

```text
notebooks/01_BBBC039_Cellpose_Benchmark_completed.ipynb
scripts/evaluate_bbbc039_final_test.py
reports/final_test/final_test_summary.csv
reports/final_test/final_test_per_image.csv
reports/final_test/final_test_worst_images.csv
reports/final_test/final_test_run_config.json
environment-final-test.yml
requirements-final-test.txt
```

The full local prediction archive is stored below `results/final_test/` and excluded from Git through `.gitignore`.

The model checksum generated during the final run is recorded in:

```text
reports/final_test/final_test_run_config.json
```

## Ethical and scientific considerations

This model is a quantitative research tool, not a source of biological truth. Users should visually inspect masks, define consistent inclusion criteria, test representative images, and validate performance before drawing biological conclusions.

No unpublished research images or proprietary model weights from the author's previous laboratory work were used in this public benchmark.

## Author

**Manh Tin Ho**  
Applied AI bioimage analysis portfolio  
Email: homanhtin@gmail.com
