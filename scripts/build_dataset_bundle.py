"""Rebuild the shipped model bundle from a validated workbook.

Run from the repository root with the research/base requirements installed:
    python scripts/build_dataset_bundle.py data/source/dataset_madura_bersih.xlsx
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wisata_madura.data import (
    BUNDLE_COLUMNS, BUNDLE_MISSING_FLAGS, REQUIRED, load_reviews, load_bundled_reviews,
)


def build_bundle(source, destination, part_size=16000):
    data = load_reviews(source)
    bundle = data[list(BUNDLE_COLUMNS)].copy()
    bundle["duplikat_persis"] = data.duplicated(subset=list(REQUIRED)).astype(int)
    bundle["tanggal_relatif"] = data.date.astype(str).str.contains(r"\blalu\b", case=False, regex=True).astype(int)
    bundle["indikasi_encoding"] = data.text_original.fillna("").astype(str).str.contains(
        r"ðŸ|â€¦|Ã©|�", case=False, regex=True).astype(int)
    for column, flag in BUNDLE_MISSING_FLAGS.items():
        bundle[flag] = data[column].isna().astype(int)
    manifest = {
        "schema_version": 1,
        "source_workbook": source.name,
        "source_workbook_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "rows": len(bundle),
        "destinations": bundle.id_destinasi.nunique(),
        "parts": [],
    }
    destination.mkdir(parents=True, exist_ok=True)
    # Validate a complete staged bundle before replacing the previous version.
    with tempfile.TemporaryDirectory(dir=destination) as temporary:
        stage = Path(temporary)
        for number, start in enumerate(range(0, len(bundle), part_size), 1):
            frame = bundle.iloc[start:start + part_size]
            name = f"ulasan_model_{number:02d}.csv.gz"
            content = gzip.compress(frame.to_csv(index=False).encode("utf-8"), mtime=0)
            (stage / name).write_bytes(content)
            manifest["parts"].append({"file": name, "rows": len(frame), "sha256": hashlib.sha256(content).hexdigest()})
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        load_bundled_reviews(stage)
        for part in manifest["parts"]:
            (stage / part["file"]).replace(destination / part["file"])
        (stage / "manifest.json").replace(destination / "manifest.json")
        current = {part["file"] for part in manifest["parts"]}
        for old in destination.glob("ulasan_model_*.csv.gz"):
            if old.name not in current:
                old.unlink()
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    print(json.dumps(build_bundle(args.source, args.output), indent=2))
