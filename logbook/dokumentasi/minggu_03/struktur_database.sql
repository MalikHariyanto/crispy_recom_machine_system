-- Schema SQLite; id_ulasan adalah tambahan untuk primary key.
CREATE TABLE ulasan (
    id_ulasan INTEGER PRIMARY KEY,
    id_destinasi INTEGER,
    destinasi TEXT,
    rating REAL,
    date TEXT,
    text_original TEXT,
    text_preprocessed TEXT,
    rekomendasi_cuaca TEXT,
    wisata TEXT
);
CREATE INDEX idx_ulasan_destinasi ON ulasan(id_destinasi);
