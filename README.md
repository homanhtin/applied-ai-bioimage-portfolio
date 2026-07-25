# Applied AI for Bioimage Analysis - Manh Tin Ho

A public portfolio demonstrating how a wet-lab cell biologist can identify an analysis bottleneck, apply an AI model, validate its performance, and package the workflow reproducibly.

[Download the portfolio PDF](docs/Applied_AI_Bioimage_Portfolio_Manh_Tin_Ho.pdf)

## Why this portfolio exists

Modern scientist roles increasingly combine experimental biology with Python, quantitative imaging, machine-learning-assisted analysis, data quality, and reproducible documentation. This repository presents evidence for those capabilities without disclosing unpublished research data.

## Evidence at a glance

### Flagship real-world case: 3D cyst analysis

- Identified manual 3D cyst measurement as a major bottleneck: approximately 14,000 cysts per experiment.
- Trained Cellpose models and collaborated with the University of Bern Data Science Lab on a Napari plugin.
- Reduced analysis time from about one week of manual work by two researchers to approximately one hour.
- Established the Python environment, protocols, reusable templates, and LIMS-linked documentation.
- The analysis framework was subsequently adapted for other experimental models by collaborating groups.

The underlying data are unpublished and are therefore not included in this public repository.

### Public reproducible project: BBBC039 Cellpose benchmark

The notebook uses the Broad Bioimage Benchmark Collection BBBC039 dataset:

- 200 fluorescence microscopy fields from a U2OS chemical screen
- approximately 23,000 manually annotated nuclei
- official training, validation, and test partitions
- CC0 public-domain data

The project demonstrates:

1. public data download and provenance
2. image and annotation quality control
3. correction of disconnected same-color instance masks
4. Cellpose-SAM baseline segmentation
5. validation-based parameter selection
6. limited model fine-tuning
7. AP, AJI, IoU-threshold, and object-count evaluation
8. structured error analysis
9. locked held-out test evaluation
10. reproducible result export

## Final held-out test results

The validation-selected model was evaluated once on all 50 images in the official BBBC039 test subset, without further model or parameter adjustment.

| Metric | Final test result |
|---|---:|
| AP@0.50 | 0.934 |
| AP@0.75 | 0.871 |
| AP@0.90 | 0.641 |
| AJI | 0.936 |
| Mean absolute count error | 3.64 nuclei/image |
| Mean absolute percentage count error | 3.21% |
| Runtime on NVIDIA RTX 3060 | 48.4 seconds |
| Runtime per image | 0.97 seconds |

The test results closely matched validation performance, supporting generalization to previously unseen BBBC039 images.

The official test subset contained no empty images. False-positive behavior on empty images was therefore not evaluated on the test set. The empty validation control produced zero false-positive objects.

The final test results were not used for additional model or parameter selection.

## Final model configuration

- Base model: `cpsam_v2`
- Fine-tuning data: 40 representative images from the official training subset
- Training epochs: 100
- Final inference settings:
  - `cellprob_threshold=0.0`
  - `flow_threshold=0.4`
  - `min_size=15`

The trained weight file is approximately 1.13 GB and is not stored directly in this Git repository. See [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md) for the intended use, limitations, validation results, and reproducibility details.

## Repository structure

```text
.
|-- assets/                         # Portfolio graphics
|-- docs/                           # Case study, ethics, model card, and project plan
|-- notebooks/                      # Main Colab/Jupyter analysis
|-- reports/final_test/             # Small final-test tables and run configuration
|-- scripts/                        # Reproducible local evaluation script
|-- src/bioimage_portfolio/         # Reusable Python utilities
|-- tests/                          # Unit tests for mask decoding and metrics
|-- environment.yml                 # General project environment
|-- environment-final-test.yml      # Environment used for the final local test
|-- requirements.txt
|-- requirements-final-test.txt
|-- CITATION.cff
`-- index.html                      # Optional GitHub Pages landing page
```

Local-only folders excluded through `.gitignore`:

```text
data/       # Downloaded public dataset
models/     # Large trained weight files
results/    # Full predictions and local intermediate outputs
```

## Quick start

### Google Colab

Open the completed notebook:

```text
https://colab.research.google.com/github/homanhtin/applied-ai-bioimage-portfolio/blob/main/notebooks/01_BBBC039_Cellpose_Benchmark_completed.ipynb
```

The notebook downloads public data, performs quality control, evaluates the pretrained model, performs validation-based parameter selection, and documents limited fine-tuning.

### Local final-test evaluation

The final test was run in a separate environment to avoid mixed OpenMP runtimes.

```bash
conda env create -f environment-final-test.yml
conda activate cellpose-final-test
python scripts/evaluate_bbbc039_final_test.py
```

Required local files:

```text
data/BBBC039/
models/bbbc039_cpsam_v2_pilot40_e100
```

The script reads the official `test.txt`, loads the locked model and parameters, evaluates all 50 test images, and writes results below `results/final_test/`.

## What this proves to employers and laboratories

| Current requirement | Evidence in this portfolio |
|---|---|
| AI-enabled scientific tools | Cellpose-SAM application and fine-tuning |
| Python and quantitative analysis | Reusable modules, notebook, CSV/JSON outputs |
| Model validation | Official train/validation/test logic, AP, AJI, error analysis |
| Wet-lab integration | Biological question and assay-bottleneck framing |
| Data quality and reproducibility | QC tables, corrected mask decoding, environment files, tests, CI |
| Cross-functional collaboration | Real cyst-analysis project with a Data Science Lab |
| Scientific communication | Public case study, model card, limitations, and CV-ready summary |

## Responsible use and confidentiality

- No unpublished microscopy images, proprietary annotations, or proprietary code are included.
- The public benchmark uses BBBC039 data downloaded from official Broad Institute sources.
- The public BBBC039 annotations were created by the dataset providers, not by the repository author.
- The fine-tuned model is validated only for the benchmark conditions represented by 2D Hoechst-stained U2OS nuclei.
- Performance on other cell types, stains, microscopes, acquisition settings, or biological structures must be validated separately.
- Model output should be treated as a measurement method requiring quality control, not as biological truth.
- The final test results are locked and were not used for further tuning.

## Data and software sources

- BBBC039, Broad Bioimage Benchmark Collection
- Cellpose / Cellpose-SAM
- NumPy, SciPy, pandas, scikit-image, tifffile, and PyTorch
- EMBL-EBI BioImage Archive machine-learning training materials

## Author

**Manh Tin Ho**  
Cell biology | CRISPR/Cas9 | 2D/3D in vitro models | Quantitative microscopy | Applied AI bioimage analysis  
Email: homanhtin@gmail.com  
LinkedIn: https://www.linkedin.com/in/manh-tin-ho
