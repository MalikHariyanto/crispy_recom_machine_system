"""01–03 · Baca workbook, audit kolom, dan pisahkan destinasi."""

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd


SHEET = "Data Ulasan"
TARGETS = ("rekomendasi_cuaca", "wisata")
REQUIRED = (
    "id_destinasi", "destinasi", "rating", "date", "text_original",
    "text_preprocessed", *TARGETS,
)


BUNDLE_COLUMNS = ("id_destinasi", "destinasi", *TARGETS, "teks_model")
BUNDLE_FLAGS = {
    "exact_duplicate_rows": "duplikat_persis",
    "relative_date_rows": "tanggal_relatif",
    "potential_encoding_error_rows": "indikasi_encoding",
}
BUNDLE_MISSING_FLAGS = {
    "text_original": "teks_asli_kosong",
    "text_preprocessed": "teks_olahan_kosong",
    "date": "tanggal_kosong",
    "rating": "rating_kosong",
}


@dataclass
class ReviewSplit:
    train: pd.DataFrame
    test: pd.DataFrame
    audit: dict


def normalize_text(text):
    """Seragamkan teks yang sudah diproses tanpa membuang kata negasi."""
    return (
        text.fillna("").astype(str).str.normalize("NFKC").str.casefold()
        .str.replace(r"[\W_]+", " ", regex=True).str.strip()
    )


def load_reviews(path: Path) -> pd.DataFrame:
    with pd.ExcelFile(path) as workbook:
        if SHEET in workbook.sheet_names:
            sheet = SHEET
        elif len(workbook.sheet_names) == 1:
            sheet = workbook.sheet_names[0]
        else:
            raise ValueError(f"Workbook harus memiliki sheet {SHEET!r} atau tepat satu sheet data.")
        data = pd.read_excel(workbook, sheet_name=sheet)
    _validate_schema(data, REQUIRED)
    return data.assign(teks_model=normalize_text(data["text_preprocessed"]))


def _validate_schema(data: pd.DataFrame, required) -> None:
    missing = sorted(set(required) - set(data.columns))
    if missing:
        raise ValueError(f"Kolom data wajib belum tersedia: {missing}")
    keys = ["id_destinasi", "destinasi", *TARGETS]
    if data.empty or any(data[key].fillna("").astype(str).str.strip().eq("").any() for key in keys):
        raise ValueError("Dataset kosong atau ada ID, nama destinasi, atau label yang kosong.")

    # ID bertipe teks agar format sama dengan CSV penilaian rekomendasi.
    data["id_destinasi"] = data["id_destinasi"].astype(str).str.strip()
    for column in ("destinasi", *TARGETS):
        data[column] = data[column].astype(str).str.strip()

    variations = data.groupby("id_destinasi")[["destinasi", *TARGETS]].nunique()
    conflicts = variations.index[variations.gt(1).any(axis=1)].tolist()
    if conflicts:
        raise ValueError(f"Nama atau label tidak konsisten untuk ID destinasi: {conflicts[:8]}")


def load_bundled_reviews(directory: Path) -> tuple[pd.DataFrame, dict]:
    """Baca data model yang ikut dalam repo dan periksa integritas tiap bagian."""
    manifest_path = directory / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Paket data tidak ditemukan di {directory}. Perbarui checkout dari cabang riset.")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or not manifest.get("parts"):
        raise ValueError("Skema manifest paket data tidak didukung.")

    required = (*BUNDLE_COLUMNS, *BUNDLE_FLAGS.values(), *BUNDLE_MISSING_FLAGS.values())
    frames = []
    for part in manifest["parts"]:
        path = directory / part["file"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != part["sha256"]:
            raise ValueError(f"Bagian paket data hilang atau rusak: {path.name}")
        frame = pd.read_csv(path, dtype={"id_destinasi": str, "teks_model": str}, keep_default_na=False)
        if set(required) - set(frame.columns) or len(frame) != part["rows"]:
            raise ValueError(f"Skema atau jumlah baris tidak cocok: {path.name}")
        frames.append(frame)

    data = pd.concat(frames, ignore_index=True)
    _validate_schema(data, required)
    if len(data) != manifest["rows"] or data["id_destinasi"].nunique() != manifest["destinations"]:
        raise ValueError("Jumlah ulasan atau destinasi berbeda dari manifest paket data.")
    if not data[[*BUNDLE_FLAGS.values(), *BUNDLE_MISSING_FLAGS.values()]].isin([0, 1]).all().all():
        raise ValueError("Penanda audit dalam paket data harus bernilai 0 atau 1.")

    return data, manifest


def audit_bundled_reviews(data: pd.DataFrame, manifest: dict) -> dict:
    """Ringkas penanda yang dihitung dari workbook sebelum kolom mentah dihilangkan."""
    empty_counts = dict.fromkeys(REQUIRED, 0)
    empty_counts.update({name: int(data[flag].sum()) for name, flag in BUNDLE_MISSING_FLAGS.items()})
    return {
        "input_mode": "bundled_model_data",
        "source_workbook_sha256": manifest["source_workbook_sha256"],
        "package_parts_sha256": [part["sha256"] for part in manifest["parts"]],
        "rows": len(data),
        "destinations": data["id_destinasi"].nunique(),
        "empty_by_column": empty_counts,
        "empty_normalized_text_rows": int(data["teks_model"].eq("").sum()),
        **{name: int(data[flag].sum()) for name, flag in BUNDLE_FLAGS.items()},
        "targets": list(TARGETS),
    }


def audit_reviews(data: pd.DataFrame, path: Path) -> dict:
    raw = data["text_original"].fillna("").astype(str)
    relative = data["date"].astype(str).str.contains(r"\blalu\b", case=False, regex=True)
    return {
        "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": len(data),
        "destinations": data["id_destinasi"].nunique(),
        "empty_by_column": {col: int(data[col].isna().sum()) for col in REQUIRED},
        "exact_duplicate_rows": int(data.duplicated(subset=list(REQUIRED)).sum()),
        "empty_normalized_text_rows": int(data["teks_model"].eq("").sum()),
        "relative_date_rows": int(relative.sum()),
        "potential_encoding_error_rows": int(raw.str.contains(r"ðŸ|â€¦|Ã©|�", case=False, regex=True).sum()),
        "targets": list(TARGETS),
    }


def label_distribution(data: pd.DataFrame) -> pd.DataFrame:
    tables = []
    for target in TARGETS:
        counts = data.groupby(target).agg(
            ulasan=("id_destinasi", "size"), destinasi=("id_destinasi", "nunique")
        )
        tables.append(counts.reset_index(names="kelas").assign(target=target))
    return pd.concat(tables, ignore_index=True)[["target", "kelas", "ulasan", "destinasi"]]


def split_reviews(data: pd.DataFrame, test_fraction=0.20, seed=42) -> ReviewSplit:
    """Pilih ID uji di tiap jenis wisata, kemudian buang teks yang bocor ke uji."""
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction harus berada di antara 0 dan 1.")

    nonempty = data.loc[data["teks_model"].ne("")]
    unique = nonempty.drop_duplicates(["id_destinasi", "teks_model"])
    # Urutan ID numerik mengikuti eksperimen sebelumnya; ID lain tetap didukung.
    ids = unique[["id_destinasi", "wisata"]].drop_duplicates()
    numeric_ids = pd.to_numeric(ids["id_destinasi"], errors="coerce")
    if numeric_ids.notna().all():
        ids = ids.assign(sort_id=numeric_ids).sort_values(["sort_id", "id_destinasi"])
    else:
        ids = ids.sort_values("id_destinasi")

    rng = np.random.default_rng(seed)
    test_ids = set()
    for _, group in ids.groupby("wisata", sort=True):
        members = group["id_destinasi"].to_numpy()
        if len(members) >= 2:
            size = min(len(members) - 1, max(1, round(len(members) * test_fraction)))
            test_ids.update(rng.choice(members, size=size, replace=False))

    is_test = unique["id_destinasi"].isin(test_ids)
    train = unique.loc[~is_test].reset_index(drop=True)
    test_raw = unique.loc[is_test]
    test = test_raw.loc[~test_raw["teks_model"].isin(train["teks_model"])].reset_index(drop=True)
    if train.empty or test.empty:
        raise ValueError("Pembagian berdasarkan destinasi menghasilkan bagian latih atau uji kosong.")
    for target in TARGETS:
        if train[target].nunique() < 2 or set(test[target]) - set(train[target]):
            raise ValueError(f"Pembagian belum dapat mengevaluasi target {target}.")

    return ReviewSplit(train, test, {
        "seed": seed,
        "requested_test_fraction": test_fraction,
        "duplicates_within_destination_removed": len(nonempty) - len(unique),
        "test_text_overlap_removed": len(test_raw) - len(test),
        "train_reviews": len(train),
        "test_reviews": len(test),
        "train_destinations": train["id_destinasi"].nunique(),
        "test_destinations": test["id_destinasi"].nunique(),
        "heldout_destinations_without_evaluable_reviews": len(test_ids) - test["id_destinasi"].nunique(),
        "classes_absent_from_test": {
            target: sorted(set(train[target]) - set(test[target])) for target in TARGETS
        },
    })


MADURA_DISTRICTS = ("Bangkalan", "Sampang", "Pamekasan", "Sumenep")


def region_template(data: pd.DataFrame) -> pd.DataFrame:
    """Daftar ID untuk verifikasi manual. Kolom kabupaten mulai dari kosong."""
    return (
        data[["id_destinasi", "destinasi"]].drop_duplicates("id_destinasi")
        .sort_values("id_destinasi").assign(kabupaten="")
    )


def select_madura_reviews(data: pd.DataFrame, path: Path) -> tuple[pd.DataFrame, dict]:
    """Ambil destinasi dengan kabupaten yang sudah diverifikasi melalui CSV."""
    mapping = pd.read_csv(path, dtype=str, keep_default_na=False)
    if not {"id_destinasi", "kabupaten"}.issubset(mapping.columns):
        raise ValueError("CSV wilayah harus memiliki kolom id_destinasi dan kabupaten.")
    ids = mapping["id_destinasi"].str.strip()
    districts = mapping["kabupaten"].str.strip().str.casefold()
    if ids.eq("").any() or ids.duplicated().any():
        raise ValueError("Gunakan satu ID yang tidak kosong untuk setiap destinasi pada CSV wilayah.")
    source_ids = set(data["id_destinasi"])
    unknown = set(ids) - source_ids
    if unknown:
        raise ValueError(f"ID pada CSV wilayah tidak ada di workbook: {sorted(unknown)[:8]}")

    accepted = {district.casefold(): district for district in MADURA_DISTRICTS}
    outside = "di luar madura"
    invalid = set(districts) - {"", outside, *accepted}
    if invalid:
        raise ValueError(f"Isi kabupaten dengan nama kabupaten Madura, Di luar Madura, atau kosong: {sorted(invalid)}")
    verified = districts.isin(accepted)
    selected = data.loc[data["id_destinasi"].isin(ids[verified])].copy()
    if selected.empty:
        raise ValueError("Belum ada ID yang ditandai sebagai destinasi di Madura pada CSV wilayah.")

    by_district = districts[verified].map(accepted).value_counts().sort_index().to_dict()
    return selected, {
        "scope": "madura_verified_ids",
        "region_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "source_destinations": len(source_ids),
        "verified_madura_by_district": {name: int(count) for name, count in by_district.items()},
        "outside_madura": int(districts.eq(outside).sum()),
        "unverified_destinations": len(source_ids) - int(verified.sum()) - int(districts.eq(outside).sum()),
    }


@dataclass
class ExperimentSplit:
    """Tiga partisi; validation dipakai untuk pemilihan model, test hanya evaluasi akhir."""
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame
    audit: dict


def validation_split(outer: ReviewSplit, fraction=0.20, seed=142) -> ExperimentSplit:
    inner = split_reviews(outer.train, test_fraction=fraction, seed=seed)
    frames = (inner.train, inner.test, outer.test)
    for i, left in enumerate(frames):
        for right in frames[i + 1:]:
            if not set(left.id_destinasi).isdisjoint(right.id_destinasi):
                raise ValueError("ID destinasi bocor antarpartisi.")
            if not set(left.teks_model).isdisjoint(right.teks_model):
                raise ValueError("Teks identik bocor antarpartisi.")
    audit = {
        "outer_split": outer.audit,
        "validation_split": inner.audit,
        "partition_reviews": dict(zip(("train", "validation", "test"), map(len, frames))),
        "partition_destinations": dict(zip(
            ("train", "validation", "test"), (f.id_destinasi.nunique() for f in frames)
        )),
        "validation_seed": seed,
        "protocol": "fit train only; select on validation; evaluate once on test",
    }
    return ExperimentSplit(inner.train, inner.test, outer.test, audit)
