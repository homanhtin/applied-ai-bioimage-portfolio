# Public Case Study: Reproducible Cellpose Benchmark on BBBC039

## Scientific problem

Chemically perturbed cells can show substantial variation in nuclear morphology, intensity, density, and overlap. A segmentation model used for screening must be evaluated across that variation rather than on a few visually convenient images.

## Objective

Evaluate a pretrained Cellpose-SAM model and a limited fine-tuned model on manually annotated U2OS nuclei, using a validation set for parameter selection and a held-out test set for final reporting.

## Dataset

BBBC039 contains 200 Hoechst-stained U2OS microscopy fields from a chemical screen and approximately 23,000 manually annotated nuclei. It provides train, validation, and test metadata and is released under CC0.

## Workflow

1. Download data from official Broad Institute URLs.
2. Decode colour-encoded instance masks.
3. Run data and annotation quality control.
4. Apply a pretrained Cellpose-SAM model.
5. Evaluate with Average Precision, Aggregated Jaccard Index, foreground IoU, and object-count error.
6. Select thresholds using validation data only.
7. Fine-tune on a limited annotated training subset.
8. Compare baseline and fine-tuned performance.
9. Review worst cases by nuclear density, morphology, illumination, and touching objects.
10. Export machine-readable CSV and JSON reports.

## Evidence produced

- Executable notebook
- Reusable Python functions
- Unit tests
- GitHub Actions CI
- Environment definitions
- Parameter-sweep table
- Error-analysis table
- Reproducible result summary

## Limitations

The public dataset contains 2-D nuclei, whereas the previous real-world cyst project involved 3-D biological structures. The public project demonstrates transferable workflow design and validation rather than claiming equivalence between the biological systems.
