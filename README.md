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
- official train, validation, and test partitions
- CC0 public-domain data

The project demonstrates:

1. public data download and provenance
2. image and annotation quality control
3. Cellpose-SAM baseline segmentation
4. validation-based parameter selection
5. limited model fine-tuning
6. AP, AJI, IoU, and object-count evaluation
7. structured error analysis
8. reproducible result export

## Repository structure

```text
.
├── notebooks/                    # Main Colab/Jupyter analysis
├── src/bioimage_portfolio/       # Reusable Python utilities
├── tests/                        # Unit tests for mask decoding and metrics
├── docs/                         # Case study, ethics, and project plan
├── assets/                       # Portfolio graphics
├── .github/workflows/            # Continuous integration
├── requirements.txt
├── environment.yml
├── CITATION.cff
└── index.html                    # Optional GitHub Pages landing page
```

## Quick start

### Google Colab

1. Upload this repository to GitHub.
2. Open `notebooks/01_BBBC039_Cellpose_Benchmark.ipynb`.
3. Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPOSITORY` in the Colab link below after publishing:

```text
https://colab.research.google.com/github/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY/blob/main/notebooks/01_BBBC039_Cellpose_Benchmark.ipynb
```

### Local environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
pytest
```

## What this proves to employers and laboratories

| Current requirement | Evidence in this portfolio |
|---|---|
| AI-enabled scientific tools | Cellpose-SAM application and fine-tuning |
| Python and quantitative analysis | Reusable modules, notebook, CSV/JSON outputs |
| Model validation | Train/validation/test logic, AP, AJI, IoU, error analysis |
| Wet-lab integration | Biological question and assay-bottleneck framing |
| Data quality and reproducibility | QC tables, fixed seed, environment files, unit tests, CI |
| Cross-functional collaboration | Real cyst-analysis project with a Data Science Lab |
| Scientific communication | Public case study, documented limitations, CV-ready summary |

## Responsible use and confidentiality

- No unpublished microscopy images, annotations, model weights, or proprietary code are included.
- Public data are downloaded from official Broad Institute URLs.
- Performance claims must only be added after the notebook has been run and reviewed.
- Model output should be treated as a measurement method requiring validation, not as biological truth.

## Data and software sources

- BBBC039, Broad Bioimage Benchmark Collection
- Cellpose documentation and software
- EMBL-EBI BioImage Archive machine-learning training materials

## Author

**Manh Tin Ho**  
Cell biology | CRISPR/Cas9 | 2D/3D in vitro models | Quantitative microscopy | Applied AI bioimage analysis  
Email: homanhtin@gmail.com  
LinkedIn: https://www.linkedin.com/in/manh-tin-ho
