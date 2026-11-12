import unittest
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from wisata_madura.data import load_reviews
from wisata_madura.tuning import grouped_folds,TuningConfig,validate_independent_data,select_configuration
from wisata_madura.neural import ReviewBiLSTM

ROOT=Path(__file__).resolve().parents[1]

class TuningTests(unittest.TestCase):
    def test_group_folds_no_overlap_and_unique_validation_groups(self):
        data=load_reviews(ROOT/'data/source/dataset_madura_bersih.xlsx')
        folds,table=grouped_folds(data,TuningConfig())
        seen=set()
        for train,valid in folds:
            ids=set(valid.id_destinasi)
            self.assertTrue(ids.isdisjoint(train.id_destinasi))
            self.assertTrue(ids.isdisjoint(seen));seen|=ids
            self.assertTrue(set(train.teks_model).isdisjoint(valid.teks_model))
        self.assertEqual(seen,set(table.loc[~table.train_only,'id_destinasi']))
        with self.assertRaises(ValueError):validate_independent_data(data,data)
        altered=data.copy();altered.id_destinasi='new'+altered.id_destinasi
        with self.assertRaises(ValueError):validate_independent_data(data,altered)

    def test_finetuning_does_not_mutate_shared_embedding_cache(self):
        vectors=np.arange(24,dtype=np.float32).reshape(6,4)
        before=vectors.copy()
        model=ReviewBiLSTM(vectors,{'a':2},4,0,freeze_embeddings=False)
        with torch.no_grad():model.embedding.weight.add_(1)
        np.testing.assert_array_equal(vectors,before)
        second=ReviewBiLSTM(vectors,{'a':2},4,0,freeze_embeddings=False)
        np.testing.assert_array_equal(second.embedding.weight.detach().numpy(),before)

    def test_deep_selection_does_not_claim_to_beat_stronger_baseline(self):
        summary=pd.DataFrame([
            dict(candidate='baseline',model='tfidf_linear_svc',validation_macro_f1_mean=.4,validation_macro_f1_std=.1),
            dict(candidate='compact',model='fasttext_bilstm',validation_macro_f1_mean=.2,validation_macro_f1_std=.1)])
        result=select_configuration(summary)
        self.assertEqual(result['model'],'fasttext_bilstm')
        self.assertEqual(result['best_observed_validation_method'],'tfidf_linear_svc')
        self.assertFalse(result['outperforms_best_baseline'])
        self.assertFalse(result['deployment_ready'])
