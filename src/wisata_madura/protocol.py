"""Predeclared group split using metadata only, never model performance."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json

import numpy as np
import pandas as pd

from .data import TARGETS, ExperimentSplit


@dataclass(frozen=True)
class SplitConfig:
    seed: int = 42
    test_fraction: float = .20
    validation_fraction: float = .16  # fraction of the complete dataset
    candidates: int = 2048


def make_experiment_split(reviews, config=None, output_dir=None):
    config = config or SplitConfig()
    fractions = np.array([1-config.test_fraction-config.validation_fraction,
                          config.validation_fraction, config.test_fraction])
    if np.any(fractions <= 0) or config.candidates < 1:
        raise ValueError('Gunakan rasio positif dengan jumlah <1 dan candidates>=1.')
    nonempty = reviews.loc[reviews.teks_model.str.strip().ne('')]
    clean = nonempty.drop_duplicates(['id_destinasi', 'teks_model']).reset_index(drop=True)
    groups = (clean.groupby('id_destinasi', sort=True)
              .agg(n=('teks_model', 'size'), wisata=('wisata', 'first'),
                   rekomendasi_cuaca=('rekomendasi_cuaca', 'first')).reset_index())
    if len(groups) < 5:
        raise ValueError('Terlalu sedikit destinasi untuk train/validation/test yang bermakna.')
    strata = [np.flatnonzero(groups.wisata.eq(label)) for label in sorted(groups.wisata.unique())]
    counts = groups.n.to_numpy()
    weather = pd.get_dummies(groups.rekomendasi_cuaca, dtype=float).to_numpy()
    rng = np.random.default_rng(config.seed)
    best = None
    for candidate in range(config.candidates):
        assignment = np.zeros(len(groups), dtype=int)
        for members in strata:
            order = rng.permutation(members)
            # A singleton stays in train; two IDs cannot appear in all 3 partitions.
            nt = min(len(order)-1, max(1, round(len(order)*config.test_fraction))) if len(order)>1 else 0
            nv = min(len(order)-nt-1, max(1, round(len(order)*config.validation_fraction))) if len(order)>2 else 0
            assignment[order[:nt]] = 2
            assignment[order[nt:nt+nv]] = 1
        if any(not np.any(assignment == i) for i in range(3)):
            continue
        if any(set(groups.loc[assignment != 0, target]) - set(groups.loc[assignment == 0, target]) for target in TARGETS):
            continue
        mass = np.bincount(assignment, weights=counts, minlength=3) / counts.sum()
        weather_mass = np.vstack([weather[assignment==i].sum(axis=0) for i in range(3)])
        weather_target = fractions[:, None]*weather.sum(axis=0)
        objective = float(np.abs(mass-fractions).sum() + .1*np.abs(weather_mass-weather_target).sum()/len(groups))
        if best is None or objective < best[0]:
            best = objective, assignment.copy(), candidate
    if best is None:
        raise ValueError('Tidak ada split valid dengan semua kelas di train. Tinjau jumlah kelompok per kelas.')
    objective, assignment, candidate = best
    mapping = dict(zip(groups.id_destinasi, assignment))
    frames, seen, removed = [], set(), {}
    names = ('train', 'validation', 'test')
    for index, name in enumerate(names):
        raw = clean.loc[clean.id_destinasi.map(mapping).eq(index)]
        frame = raw.loc[~raw.teks_model.isin(seen)].reset_index(drop=True)
        removed[name] = len(raw)-len(frame)
        seen.update(frame.teks_model)
        if frame.empty:
            raise ValueError(f'Partisi {name} kosong setelah membuang teks identik lintas kelompok.')
        frames.append(frame)
    for target in TARGETS:
        if set(clean[target]) - set(frames[0][target]):
            raise ValueError(f'Kelas {target} hilang dari train setelah pembersihan.')
    coverage = []
    for target in TARGETS:
        for label in sorted(clean[target].unique()):
            row = dict(target=target, kelas=label)
            for name, frame in zip(names, frames):
                row[name+'_destinasi'] = int(frame.loc[frame[target].eq(label), 'id_destinasi'].nunique())
            coverage.append(row)
    audit = dict(
        config=asdict(config), selected_candidate=int(candidate), metadata_objective=objective,
        protocol='group split before fitting; metadata-only selection; fit train/select validation/evaluate test',
        selection_uses='destination ID, group size, wisata/cuaca strata; no text features/model scores',
        input_reviews=len(reviews), empty_removed=len(reviews)-len(nonempty),
        duplicates_within_destination_removed=len(nonempty)-len(clean),
        cross_partition_text_removed=removed,
        partition_reviews=dict(zip(names, map(len, frames))),
        partition_destinations=dict(zip(names, (f.id_destinasi.nunique() for f in frames))),
        assigned_destinations=dict(zip(names, (int((assignment==i).sum()) for i in range(3)))),
        class_coverage=coverage,
        limitations='Singleton classes remain train-only. Fixed holdout of 27 destinations has high uncertainty. Metadata balancing is not evidence of unbiased generalization.',
    )
    result = ExperimentSplit(*frames, audit)
    if output_dir is not None:
        output = Path(output_dir); output.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(coverage).to_csv(output/'cakupan_kelas_partisi.csv', index=False)
        for name, frame in zip(names, frames):
            frame[['id_destinasi','destinasi',*TARGETS]].drop_duplicates().to_csv(output/f'id_partisi_{name}.csv', index=False)
        (output/'audit_split.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
    return result


def destination_sample_weights(frame):
    """Every destination has equal total weight; mean review weight is one."""
    sizes = frame.groupby('id_destinasi').id_destinasi.transform('size')
    weights = 1.0/sizes.to_numpy(dtype=float)
    return weights/weights.mean()
