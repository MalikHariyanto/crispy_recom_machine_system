"""Regression checks for ranking, session scope, and geographic verification."""
import unittest
import pandas as pd
from wisata_madura.web.services import SearchIndex, filter_catalog, read_regions


class WebServicesTests(unittest.TestCase):
    def setUp(self):
        self.catalog = pd.DataFrame([
            {"id_destinasi": "1", "destinasi": "Pantai", "deskripsi": "pantai pasir putih laut", "wisata": "Alam", "rekomendasi_cuaca": "Kemarau", "kabupaten": "Sumenep"},
            {"id_destinasi": "2", "destinasi": "Museum", "deskripsi": "museum sejarah budaya", "wisata": "Budaya", "rekomendasi_cuaca": "Kemarau & Penghujan", "kabupaten": "Belum diverifikasi"},
            {"id_destinasi": "3", "destinasi": "Pantai lain", "deskripsi": "pantai pasir laut", "wisata": "Alam", "rekomendasi_cuaca": "Kemarau & Penghujan", "kabupaten": "Di luar Madura"},
        ])
        self.index = SearchIndex(self.catalog)

    def test_query_ranks_relevant_destination_and_drops_zero_overlap(self):
        result = self.index.search("pasir putih", self.catalog.id_destinasi)
        self.assertEqual(list(result.id_destinasi), ["1", "3"])
        self.assertTrue(self.index.search("qzxwvu", self.catalog.id_destinasi).empty)

    def test_scope_and_history_cannot_leak_into_ranking(self):
        result = self.index.search("pantai", ["1", "2"], excluded=["1"])
        self.assertTrue(result.empty)
        self.assertTrue(self.index.search("pantai", []).empty)

    def test_filters_respect_weather_and_verified_region(self):
        result = filter_catalog(self.catalog, season="Penghujan")
        self.assertEqual(set(result.id_destinasi), {"2", "3"})
        self.assertEqual(list(filter_catalog(self.catalog, verified_only=True).id_destinasi), ["1"])
        self.assertTrue(filter_catalog(self.catalog, name="[x]").empty)

    def test_region_csv_rejects_unknown_ids_duplicates_and_invalid_labels(self):
        for value in [b'id_destinasi,kabupaten\n9,Sumenep', b'id_destinasi,kabupaten\n1,Sumenep\n1,Sumenep',
                      b'id_destinasi,kabupaten\n1,Surabaya', b'wrong,column\n1,2']:
            with self.assertRaises(ValueError):
                read_regions(value, ["1", "2"])
        valid = read_regions(b'id_destinasi,kabupaten\n1, sumenep \n2,', ["1", "2"])
        self.assertEqual(list(valid.kabupaten), ["Sumenep", ""])


if __name__ == "__main__":
    unittest.main()
