"""Fetch the reference dataset — the CASAS (WSU) Aruba home.

The labeled Aruba recording ships in the CASAS Zenodo record 17180309
("CASAS Smart Home dataset (aruba, cairo, milan, tulum) - free living,
motion, door, temperature, activity labels", license CC BY 4.0 — verified
from the record's own metadata; see DATA_NOTES.md). The zip also carries
the Cairo, Milan, and Tulum homes for future adapters.

Note: the larger CASAS free-living corpus (record 15708568) contains an
*unlabeled* aruba.csv — same home, no activity annotations. HouseRules
needs the labels (they anchor tasks and supply occupancy/sleep context),
so it uses record 17180309. The distinction is documented in DATA_NOTES.md.

    houserules fetch-data [--data-dir DIR]

Default data dir: $HOUSERULES_DATA, else ./data, else ~/.cache/houserules.
"""

from __future__ import annotations

import hashlib
import os
import urllib.request
import zipfile
from pathlib import Path

ZENODO_RECORD = "17180309"
ZENODO_FILE = "new_labeled_data.zip"
ZENODO_URL = f"https://zenodo.org/api/records/{ZENODO_RECORD}/files/{ZENODO_FILE}/content"
ZENODO_MD5 = "86954063e1d2099d288f59227b19a749"
DOI = "10.5281/zenodo.17180309"


def default_data_dir() -> Path:
    env = os.environ.get("HOUSERULES_DATA")
    if env:
        return Path(env)
    local = Path.cwd() / "data"
    if local.parent.exists():
        return local
    return Path.home() / ".cache" / "houserules"


def aruba_path(data_dir: Path) -> Path:
    return Path(data_dir) / "aruba.txt"


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_data(data_dir: Path | None = None, force: bool = False) -> Path:
    """Download (if needed) and extract the Aruba home. Returns its path."""
    data_dir = Path(data_dir) if data_dir else default_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    target = aruba_path(data_dir)
    if target.exists() and not force:
        return target
    zip_path = data_dir / ZENODO_FILE
    if not zip_path.exists() or force:
        print(f"Downloading the CASAS labeled testbed record from Zenodo "
              f"(record {ZENODO_RECORD}, DOI {DOI}) ...")
        urllib.request.urlretrieve(ZENODO_URL, zip_path)
    digest = _md5(zip_path)
    if digest != ZENODO_MD5:
        raise SystemExit(
            f"Checksum mismatch for {ZENODO_FILE}: got {digest}, expected "
            f"{ZENODO_MD5} (as published on the Zenodo record). Refusing to "
            f"build on unverified data.")
    print(f"Checksum verified (md5 {digest}).")
    with zipfile.ZipFile(zip_path) as zf:
        candidates = [n for n in zf.namelist()
                      if "aruba" in n.lower() and not n.endswith("/")]
        if not candidates:
            raise SystemExit("No Aruba file found inside the corpus zip.")
        candidates.sort(key=lambda n: (not n.lower().endswith(".txt"), len(n)))
        name = candidates[0]
        print(f"Extracting {name} -> {target}")
        with zf.open(name) as src, open(target, "wb") as dst:
            while True:
                chunk = src.read(1 << 20)
                if not chunk:
                    break
                dst.write(chunk)
    return target
