"""Verify the active bundle is an exact model projection of the new workbook."""
from pathlib import Path
import hashlib
import tempfile
import unittest

import pandas as pd
from wisata_madura.data import load_reviews, load_bundled_reviews, audit_reviews, audit_bundled_reviews

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/source/dataset_madura_bersih.xlsx"


class DatasetUpdateTests(unittest.TestCase):
    def test_bundle_matches_latest_workbook(self):
        raw = load_reviews(SOURCE)
        bundled, manifest = load_bundled_reviews(ROOT / "data")
        self.assertEqual((len(bundled), bundled.id_destinasi.nunique()), (2058, 27))
        self.assertEqual(manifest["source_workbook_sha256"], hashlib.sha256(SOURCE.read_bytes()).hexdigest())
        columns = ["id_destinasi", "destinasi", "wisata", "rekomendasi_cuaca", "teks_model"]
        pd.testing.assert_frame_equal(raw[columns], bundled[columns])
        source_audit, bundle_audit = audit_reviews(raw, SOURCE), audit_bundled_reviews(bundled, manifest)
        for key in ["rows", "destinations", "empty_by_column", "exact_duplicate_rows", "relative_date_rows",
                    "potential_encoding_error_rows", "empty_normalized_text_rows"]:
            self.assertEqual(source_audit[key], bundle_audit[key], key)
        self.assertEqual(set(p.name for p in (ROOT / 'data').glob('ulasan_model_*.csv.gz')),
                         set(p['file'] for p in manifest['parts']))

    def test_legacy_sheet_and_ambiguous_workbook(self):
        sample = pd.read_excel(SOURCE).head(2)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.xlsx'
            sample.to_excel(path, sheet_name='Data Ulasan', index=False)
            self.assertEqual(len(load_reviews(path)), 2)
            with pd.ExcelWriter(path) as writer:
                sample.to_excel(writer, sheet_name='Other', index=False)
                sample.to_excel(writer, sheet_name='Notes', index=False)
            with self.assertRaises(ValueError):
                load_reviews(path)
