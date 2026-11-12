"""Charts must preserve the distinction between reviews and destinations."""
from pathlib import Path
import tempfile
import unittest

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from wisata_madura.data import load_reviews, split_reviews, validation_split
from wisata_madura.visualization import plot_dataset_overview, plot_partition_overview

ROOT = Path(__file__).resolve().parents[1]


class VisualizationTests(unittest.TestCase):
    def test_actual_workbook_charts_and_split(self):
        reviews = load_reviews(ROOT / "data/source/dataset_madura_bersih.xlsx")
        with tempfile.TemporaryDirectory() as folder:
            figures, tables = plot_dataset_overview(reviews, folder)
            self.assertEqual(tables["rating"].ulasan.tolist(), [49, 43, 144, 330, 1492])
            self.assertEqual(tables["cuaca_ulasan"].ulasan.sum(), 2058)
            self.assertEqual(tables["cuaca_destinasi"].destinasi.sum(), 27)
            self.assertAlmostEqual(tables["jenis_destinasi"].persentase.sum(), 100)
            split = validation_split(split_reviews(reviews))
            figure, summary = plot_partition_overview(split, folder)
            self.assertEqual(summary.ulasan.sum(), sum(len(f) for f in (split.train, split.validation, split.test)))
            self.assertAlmostEqual(summary.persen_ulasan.sum(), 100)
            self.assertAlmostEqual(summary.persen_destinasi.sum(), 100)
            self.assertTrue((Path(folder) / "pembagian_data.png").is_file())
            for f in (*figures, figure):
                plt.close(f)
