"""Exploratory grouped tuning; this module accepts no independent test set."""
from dataclasses import dataclass, asdict, replace
from pathlib import Path
from types import SimpleNamespace
import hashlib
import json

import numpy as np
import pandas as pd

from .data import TARGETS
from .modeling import evaluate_classifiers, run_baselines


@dataclass(frozen=True)
class TuningConfig:
    folds: int = 3
    fold_seed: int = 20261112
    training_seeds: tuple = (42, 43)
    max_epochs: int = 15
    patience: int = 3
    lda_topics: tuple = (2, 4, 6)
    lda_seeds: tuple = (42, 43)
    lda_iterations: int = 10


CANDIDATES = (
    dict(name='compact', embedding_dim=80, hidden_dim=32, learning_rate=.001, dropout=.2, freeze_embeddings=True, length_quantile=.90),
    dict(name='wider', embedding_dim=128, hidden_dim=64, learning_rate=.001, dropout=.3, freeze_embeddings=True, length_quantile=.95),
    dict(name='slower', embedding_dim=128, hidden_dim=64, learning_rate=.0003, dropout=.4, freeze_embeddings=True, length_quantile=.95),
    dict(name='finetune', embedding_dim=128, hidden_dim=64, learning_rate=.0003, dropout=.4, freeze_embeddings=False, length_quantile=.95),
)


def development_fingerprint(reviews):
    columns = ['id_destinasi','destinasi','teks_model',*TARGETS]
    return hashlib.sha256(reviews[columns].to_csv(index=False).encode()).hexdigest()


def grouped_folds(reviews, config):
    """Keep singleton label groups in train; every other ID validates once."""
    if config.folds < 2:
        raise ValueError('Gunakan minimal dua fold.')
    clean = reviews.loc[reviews.teks_model.str.strip().ne('')].drop_duplicates(['id_destinasi','teks_model'])
    groups = clean[['id_destinasi',*TARGETS]].drop_duplicates('id_destinasi').sort_values('id_destinasi').reset_index(drop=True)
    anchored = set()
    for target in TARGETS:
        counts = groups[target].value_counts()
        anchored.update(groups.loc[groups[target].map(counts).eq(1),'id_destinasi'])
    rng = np.random.default_rng(config.fold_seed)
    assignments = dict.fromkeys(anchored, -1)
    offset = 0
    for _, part in groups.loc[~groups.id_destinasi.isin(anchored)].groupby('wisata',sort=True):
        ids = rng.permutation(part.id_destinasi.to_numpy())
        for i, identifier in enumerate(ids):
            assignments[identifier] = (i+offset) % config.folds
        offset = (offset+len(ids)) % config.folds
    results = []
    for fold in range(config.folds):
        valid_ids = {key for key,value in assignments.items() if value==fold}
        train = clean.loc[~clean.id_destinasi.isin(valid_ids)].reset_index(drop=True)
        validation = clean.loc[clean.id_destinasi.isin(valid_ids)]
        validation = validation.loc[~validation.teks_model.isin(train.teks_model)].reset_index(drop=True)
        if train.empty or validation.empty:
            raise ValueError('Fold kosong setelah pembersihan teks; kurangi folds atau tambah destinasi.')
        for target in TARGETS:
            if set(validation[target])-set(train[target]):
                raise ValueError('Label validation tidak ada di train; tinjau skema kelompok.')
        results.append((train,validation))
    table = groups.assign(validation_fold=groups.id_destinasi.map(assignments), train_only=groups.id_destinasi.isin(anchored))
    return results,table


def validate_independent_data(development, external):
    """Reject reused destinations/text before any future independent scoring."""
    ids = set(development.id_destinasi) & set(external.id_destinasi)
    names = set(development.destinasi.str.casefold().str.strip()) & set(external.destinasi.str.casefold().str.strip())
    texts = set(development.teks_model) & set(external.teks_model)
    unknown = {target: sorted(set(external[target])-set(development[target])) for target in TARGETS}
    if ids or names or texts or any(unknown.values()):
        raise ValueError('Data independen berbagi ID/nama/teks dengan development atau mempunyai label baru. Audit diperlukan.')
    if external.empty:
        raise ValueError('Data independen kosong.')
    return dict(status='overlap_checks_passed', independent_score_available=False,
                note='Independence also requires collection provenance and a model frozen before access.')


def run_grouped_tuning(reviews, output_dir, config=None, candidates=CANDIDATES):
    """Train/validate only. Scores select settings and are not final estimates."""
    from .topics import TopicConfig, analyze_topics
    from .neural import DeepConfig, fit_fasttext, run_bilstm_variants
    config = config or TuningConfig()
    output = Path(output_dir); output.mkdir(parents=True,exist_ok=True)
    folds, assignments = grouped_folds(reviews,config)
    plan = dict(source_module_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}, config=asdict(config), candidates=list(candidates), dataset_sha256=development_fingerprint(reviews),
                objective='mean destination macro-F1 across both targets, folds and declared seeds; tie by candidate order then model name',
                status='exploratory development only; previous holdout already observed; no independent score',
                singleton_policy='train-only, never evidence of generalization',
                selection_bias='validation reused for LDA selection, early stopping and hyperparameters; scores are optimistic selection diagnostics')
    plan_text=json.dumps(plan,indent=2,sort_keys=True)
    plan_path=output/'protocol_before_tuning.json'
    if plan_path.exists():
        raise FileExistsError('Gunakan folder run baru agar protokol dan hasil tidak tertimpa.')
    plan_path.write_text(plan_text,encoding='utf-8')
    assignments.to_csv(output/'fold_assignments.csv',index=False)
    all_metrics,coverage,checkpoints=[],[],[]
    label_space={target:sorted(reviews[target].unique()) for target in TARGETS}
    for fold,(train,valid) in enumerate(folds):
        print(f'FOLD {fold+1}/{config.folds}: train {len(train)}, validation {len(valid)} ulasan',flush=True)
        folder=output/f'fold_{fold}';folder.mkdir()
        # Deliberately no independent test object: the legacy API's test slot
        # is validation again, for validation predictions only. Never held out claims.
        split=SimpleNamespace(train=train,validation=valid,test=valid)
        topics,_,_=analyze_topics(split,folder/'lda',TopicConfig(
            topic_counts=config.lda_topics,seeds=config.lda_seeds,max_iter=config.lda_iterations))
        for target in TARGETS:
            for label in label_space[target]:
                coverage.append(dict(fold=fold,target=target,kelas=label,
                    train_destinasi=train.loc[train[target].eq(label),'id_destinasi'].nunique(),
                    validation_destinasi=valid.loc[valid[target].eq(label),'id_destinasi'].nunique()))
        baseline=run_baselines(split,seed=config.training_seeds[0])
        metrics,_=evaluate_classifiers(valid,baseline,label_space)
        all_metrics.append(metrics.assign(fold=fold,seed=config.training_seeds[0],candidate='baseline'))
        for seed in config.training_seeds:
            embedding_cache={}
            for candidate in candidates:
                quantile=candidate['length_quantile']
                max_tokens=int(np.clip(np.ceil(train.teks_model.str.split().str.len().quantile(quantile)),16,128))
                options={k:v for k,v in candidate.items() if k not in {'name','length_quantile'}}
                deep=DeepConfig(seed=seed,max_tokens=max_tokens,bilstm_epochs=config.max_epochs,patience=config.patience,**options)
                embedding_key=(deep.embedding_dim,max_tokens)
                if embedding_key not in embedding_cache:
                    embedding_cache[embedding_key]=fit_fasttext(split,deep)
                run=folder/f'seed_{seed}'/candidate['name'];run.mkdir(parents=True)
                (run/'config.json').write_text(json.dumps(asdict(deep),indent=2))
                predictions,history=run_bilstm_variants(split,topics,embedding_cache[embedding_key],deep,run)
                history.to_csv(run/'history.csv',index=False)
                metrics,_=evaluate_classifiers(valid,predictions,label_space)
                all_metrics.append(metrics.assign(fold=fold,seed=seed,candidate=candidate['name']))
                checkpoints.append(pd.read_csv(run/'checkpoint_bilstm.csv').assign(fold=fold,seed=seed,candidate=candidate['name']))
                pd.concat(all_metrics).to_csv(output/'validation_metrics.csv',index=False)
    metrics=pd.concat(all_metrics,ignore_index=True)
    # Average targets within each fold/seed first; then average these units.
    units=(metrics.loc[metrics.unit.eq('destinasi')].groupby(['candidate','model','fold','seed']).macro_f1.mean().reset_index())
    summary=units.groupby(['candidate','model']).agg(validation_macro_f1_mean=('macro_f1','mean'),
        validation_macro_f1_std=('macro_f1','std'),fold_seed_units=('macro_f1','size')).reset_index()
    summary.to_csv(output/'candidate_summary.csv',index=False)
    pd.DataFrame(coverage).to_csv(output/'class_coverage.csv',index=False)
    pd.concat(checkpoints,ignore_index=True).to_csv(output/'checkpoints.csv',index=False)
    result=select_configuration(summary,candidates)
    (output/'selected_configuration.json').write_text(json.dumps(result,indent=2))
    return summary,result


def select_configuration(summary, candidates=CANDIDATES):
    ranking=summary.loc[~summary.candidate.eq('baseline')].copy()
    ranking['order']=ranking.candidate.map({c['name']:i for i,c in enumerate(candidates)})
    winner=ranking.sort_values(['validation_macro_f1_mean','order','model'],ascending=[False,True,True]).iloc[0]
    selected=next(c for c in candidates if c['name']==winner.candidate)
    result=dict(candidate=selected,model=winner.model,selection_validation_mean=float(winner.validation_macro_f1_mean),
        selection_validation_std=float(winner.validation_macro_f1_std),
        evaluation_status='exploratory selection score only; independent evaluation pending new untouched data',
        deployment_ready=False, baselines_compared=True)
    overall=summary.sort_values(['validation_macro_f1_mean','candidate','model'],ascending=[False,True,True]).iloc[0]
    baseline=summary.loc[summary.candidate.eq('baseline'),'validation_macro_f1_mean'].max()
    result.update(selection_scope='deep candidates only; overall best reported separately',
                  best_observed_validation_method=str(overall.model),
                  best_observed_validation_mean=float(overall.validation_macro_f1_mean),
                  outperforms_best_baseline=bool(winner.validation_macro_f1_mean > baseline))
    return result
