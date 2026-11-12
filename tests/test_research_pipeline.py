"""Regression checks for leakage, topic scoring, and best-checkpoint restoration."""
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix

from wisata_madura.data import load_bundled_reviews, split_reviews, validation_split
from wisata_madura.modeling import TopicFeatures
from wisata_madura.topics import document_npmi, topic_stability, TopicConfig, analyze_topics

ROOT = Path(__file__).resolve().parents[1]


class ResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data, _ = load_bundled_reviews(ROOT / 'data')
        cls.split = validation_split(split_reviews(data))

    def test_npmi_known_probabilities(self):
        cooccur = csr_matrix([[1, 1, 0], [1, 1, 0], [0, 0, 1], [0, 0, 1]])
        self.assertAlmostEqual(document_npmi(cooccur, [[0, 1]])[0], 1)
        self.assertEqual(document_npmi(cooccur, [[0, 2]])[0], -1)
        independent = csr_matrix([[1, 1], [1, 0], [0, 1], [0, 0]])
        self.assertAlmostEqual(document_npmi(independent, [[0, 1]])[0], 0)

    def test_stability_ignores_topic_numbering(self):
        topics = [[0, 1, 2], [3, 4, 5]]
        self.assertEqual(topic_stability(topics, topics[::-1]), 1)
        self.assertEqual(topic_stability(topics, [[6, 7, 8], [9, 10, 11]]), 0)

    def test_three_partitions_no_identity_or_text_overlap(self):
        s = self.split
        for left, right in ((s.train, s.validation), (s.train, s.test), (s.validation, s.test)):
            self.assertTrue(set(left.id_destinasi).isdisjoint(right.id_destinasi))
            self.assertTrue(set(left.teks_model).isdisjoint(right.teks_model))
        self.assertGreater(s.test.id_destinasi.nunique(), 0)
        self.assertLess(s.test.id_destinasi.nunique(), s.train.id_destinasi.nunique())

    def test_selection_and_vocabulary_do_not_read_test(self):
        s = replace(self.split, train=self.split.train.head(700),
                    validation=self.split.validation.head(250), test=self.split.test.head(100))
        config = TopicConfig(topic_counts=(2, 3), seeds=(42, 43), max_iter=2,
                             top_words=3, min_df=2, per_destination=15)
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            first, tables_a, audit_a = analyze_topics(s, a, config)
            changed = replace(s, test=s.test.assign(teks_model='heldoutuniquetoken'))
            second, tables_b, audit_b = analyze_topics(changed, b, config)
            self.assertEqual(audit_a['selected_topics'], audit_b['selected_topics'])
            np.testing.assert_allclose(tables_a['pemilihan_topik'].validation_npmi_mean,
                                       tables_b['pemilihan_topik'].validation_npmi_mean)
            np.testing.assert_allclose(first.train, second.train)
            import joblib
            artifact = joblib.load(Path(b) / 'model_lda.joblib')
            self.assertNotIn('heldoutuniquetoken', artifact['vectorizer'].vocabulary_)

    def test_early_stop_restores_saved_checkpoint(self):
        import torch
        import pandas as pd
        from wisata_madura.data import ExperimentSplit, TARGETS
        from wisata_madura.neural import DeepConfig, fit_fasttext, run_bilstm_variants, ReviewBiLSTM, _features
        def frame(prefix):
            return pd.DataFrame([dict(id_destinasi=f'{prefix}{i}', destinasi=f'{prefix}{i}',
                teks_model=('pantai pasir nyaman keluarga' if i % 2 else 'gunung sejuk jalan hijau'),
                wisata=('pantai' if i % 2 else 'gunung'),
                rekomendasi_cuaca=('Kemarau' if i % 2 else 'Kemarau & Penghujan')) for i in range(8)])
        s = ExperimentSplit(frame('tr'), frame('va'), frame('te'), {})
        topics = TopicFeatures(train=np.tile([.3, .7], (8, 1)).astype('float32'),
                              validation=np.tile([.3, .7], (8, 1)).astype('float32'),
                              test=np.tile([.3, .7], (8, 1)).astype('float32'),
                              keywords=pd.DataFrame(), weather_summary=pd.DataFrame(), sample_size=8)
        config = DeepConfig(embedding_dim=8, hidden_dim=4, max_tokens=8,
                            fasttext_epochs=1, bilstm_epochs=4, batch_size=4,
                            patience=1, min_delta=1e6)
        with tempfile.TemporaryDirectory() as d:
            encoded = fit_fasttext(s, config, d)
            predictions, history = run_bilstm_variants(s, topics, encoded, config, d)
            ck = pd.read_csv(Path(d) / 'checkpoint_bilstm.csv')
            self.assertTrue(ck.best_epoch.eq(1).all())
            self.assertTrue(ck.epochs_executed.eq(2).all())
            self.assertTrue(np.isfinite(history.validation_loss).all())
            for variant in predictions:
                saved = torch.load(Path(d) / (variant + '.pt'), weights_only=True, map_location='cpu')
                model = ReviewBiLSTM(encoded.embeddings, {k: len(v) for k, v in saved['labels'].items()},
                                     config.hidden_dim, saved['topic_dim'])
                model.load_state_dict(saved['state_dict']); model.eval()
                tokens, lengths, topic_tensor = _features(encoded.test_tokens, topics.test)
                with torch.inference_mode(): logits = model(tokens.long(), lengths, topic_tensor)
                for target in TARGETS:
                    expected = np.asarray(saved['labels'][target])[logits[target].argmax(dim=1).numpy()]
                    np.testing.assert_array_equal(predictions[variant][target], expected)


if __name__ == '__main__':
    unittest.main()
