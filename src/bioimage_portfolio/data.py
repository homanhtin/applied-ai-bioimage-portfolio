from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve
import zipfile

DATA_URLS = {
    "images": "https://data.broadinstitute.org/bbbc/BBBC039/images.zip",
    "masks": "https://data.broadinstitute.org/bbbc/BBBC039/masks.zip",
    "metadata": "https://data.broadinstitute.org/bbbc/BBBC039/metadata.zip",
}


def download_bbbc039(root: str | Path) -> Path:
    """Download and extract BBBC039 from the official Broad Institute URLs."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    for name, url in DATA_URLS.items():
        archive = root / f"{name}.zip"
        target = root / name
        if not archive.exists():
            urlretrieve(url, archive)
        if not target.exists():
            target.mkdir(parents=True)
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(target)
    return root
