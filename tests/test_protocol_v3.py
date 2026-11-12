"""Regression tests for leakage controls and group-balanced accounting."""
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

from wisata_madura.data import load_reviews, TARGETS
from wisata_madura.protocol import make_experiment_split, destination_sample_weights
from wisata_madura.modeling import evaluate_classifiers

ROOT = Path(__file__).resolve().parents[1]


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reviews = load_reviews(ROOT/'data/source/dataset_madura_bersih.xlsx')
        cls.split = make_experiment_split(cls.reviews)

    def test_groups_texts_and_train_label_coverage(self):
        frames = [self.split.train, self.split.validation, self.split.test]
        for i, left in enumerate(frames):
            for right in frames[i+1:]:
                self.assertTrue(set(left.id_destinasi).isdisjoint(right.id_destinasi))
                self.assertTrue(set(left.teks_model).isdisjoint(right.teks_model))
        for target in TARGETS:
            self.assertEqual(set(self.split.train[target]), set(self.reviews[target]))
        train_share = len(frames[0])/sum(map(len,frames))
        self.assertGreater(train_share,.5)  # legacy split trained on only 18% of reviews
        self.assertLess(len(frames[2])/sum(map(len,frames)),.35)

    def test_split_reproducible_and_does_not_use_rating(self):
        again = make_experiment_split(self.reviews.assign(rating=1))
        for a,b in zip((self.split.train,self.split.validation,self.split.test),
                       (again.train,again.validation,again.test)):
            self.assertEqual(a.id_destinasi.tolist(),b.id_destinasi.tolist())

    def test_weights_give_equal_total_mass_to_destinations(self):
        frame = pd.DataFrame({'id_destinasi':['a']*100+['b']*2+['c']})
        weights = destination_sample_weights(frame)
        totals = pd.Series(weights).groupby(frame.id_destinasi).sum()
        np.testing.assert_allclose(totals, [len(frame)/3]*3)
        self.assertAlmostEqual(weights.mean(),1)

    def test_metrics_include_absent_classes_and_show_support(self):
        frame = pd.DataFrame({'id_destinasi':['1','2'], 'wisata':['pantai','pantai'],
                              'rekomendasi_cuaca':['Kemarau','Kemarau']})
        predictions={'m':{t:frame[t].to_numpy() for t in TARGETS}}
        label_space={'wisata':['pantai','hutan'], 'rekomendasi_cuaca':['Kemarau','Penghujan']}
        metrics,details=evaluate_classifiers(frame,predictions,label_space)
        np.testing.assert_allclose(metrics.macro_f1,.5)
        np.testing.assert_allclose(metrics.macro_f1_present,1)
        self.assertTrue((details.loc[details.kelas.isin(['hutan','Penghujan']),'support']==0).all())
