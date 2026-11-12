-- Jalankan pada dataset_wisata.sqlite menggunakan DB Browser -> Execute SQL.
-- Tidak mengubah atau menghapus baris ulasan. Tabel review adalah tempat isian manual.
-- Memerlukan SQLite >= 3.25 untuk ROW_NUMBER (tersedia pada DB Browser modern).
PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS m07_sampel (
    id_ulasan INTEGER PRIMARY KEY REFERENCES ulasan(id_ulasan),
    cara_pilih TEXT NOT NULL DEFAULT 'Maksimal 5 baris pertama per ID destinasi, urut id_ulasan'
);
INSERT OR IGNORE INTO m07_sampel (id_ulasan)
SELECT id_ulasan FROM (
    SELECT id_ulasan,
           ROW_NUMBER() OVER (PARTITION BY id_destinasi ORDER BY id_ulasan) AS urutan
    FROM ulasan
) WHERE urutan <= 5;

CREATE TABLE IF NOT EXISTS m07_review_sentimen (
    id_ulasan INTEGER PRIMARY KEY REFERENCES ulasan(id_ulasan),
    sentimen TEXT CHECK(sentimen IS NULL OR sentimen IN ('Positif','Netral','Negatif','Campuran/ambigu')),
    alasan TEXT,
    penilai TEXT,
    tanggal_review TEXT
);
INSERT OR IGNORE INTO m07_review_sentimen (id_ulasan)
SELECT id_ulasan FROM m07_sampel;

CREATE TABLE IF NOT EXISTS m07_review_destinasi (
    id_destinasi INTEGER PRIMARY KEY,
    status_review TEXT NOT NULL DEFAULT 'Belum ditinjau'
        CHECK(status_review IN ('Belum ditinjau','Sesuai','Perlu ditinjau')),
    alasan_keraguan TEXT,
    kategori_usulan TEXT,
    penilai TEXT,
    tanggal_review TEXT
);
INSERT OR IGNORE INTO m07_review_destinasi (id_destinasi)
SELECT DISTINCT id_destinasi FROM ulasan;

CREATE TABLE IF NOT EXISTS m07_review_waktu (
    id_ulasan INTEGER PRIMARY KEY REFERENCES ulasan(id_ulasan),
    status_waktu TEXT NOT NULL DEFAULT 'Belum diverifikasi'
        CHECK(status_waktu IN ('Belum diverifikasi','Belum diketahui','Ada bukti waktu')),
    bukti_waktu_kunjungan TEXT,
    musim_terverifikasi TEXT,
    alasan TEXT,
    penilai TEXT,
    tanggal_review TEXT
);
INSERT OR IGNORE INTO m07_review_waktu (id_ulasan)
SELECT id_ulasan FROM m07_sampel;

CREATE VIEW IF NOT EXISTS m07_01_rekap_sampel AS
SELECT u.id_destinasi, u.destinasi, COUNT(*) AS jumlah_sampel,
       MIN(s.cara_pilih) AS cara_pilih
FROM m07_sampel s JOIN ulasan u USING(id_ulasan)
GROUP BY u.id_destinasi, u.destinasi;

CREATE VIEW IF NOT EXISTS m07_02_periksa_jenis AS
SELECT u.id_destinasi, u.destinasi, u.wisata AS kategori_sumber,
       COUNT(*) AS jumlah_ulasan, r.status_review, r.alasan_keraguan,
       r.kategori_usulan
FROM ulasan u JOIN m07_review_destinasi r USING(id_destinasi)
GROUP BY u.id_destinasi, u.destinasi, u.wisata,
         r.status_review, r.alasan_keraguan, r.kategori_usulan;

CREATE VIEW IF NOT EXISTS m07_03_periksa_sentimen AS
SELECT u.id_ulasan, u.id_destinasi, u.destinasi, u.text_original,
       a.sentimen, a.alasan, a.penilai, a.tanggal_review
FROM m07_sampel s JOIN ulasan u USING(id_ulasan)
JOIN m07_review_sentimen a USING(id_ulasan);

CREATE VIEW IF NOT EXISTS m07_04_periksa_waktu AS
SELECT u.id_ulasan, u.destinasi, u.date AS tanggal_sumber,
       u.text_original, r.status_waktu, r.bukti_waktu_kunjungan,
       r.musim_terverifikasi, r.alasan
FROM m07_sampel s JOIN ulasan u USING(id_ulasan)
JOIN m07_review_waktu r USING(id_ulasan);

CREATE VIEW IF NOT EXISTS m07_05_distribusi_jenis AS
SELECT wisata AS kategori_sumber, COUNT(*) AS jumlah_ulasan,
       COUNT(DISTINCT id_destinasi) AS jumlah_destinasi
FROM ulasan GROUP BY wisata;

CREATE VIEW IF NOT EXISTS m07_05_status_review AS
SELECT 'Destinasi' AS bagian, status_review AS status, COUNT(*) AS jumlah
FROM m07_review_destinasi GROUP BY status_review
UNION ALL
SELECT 'Sentimen', CASE WHEN sentimen IS NULL THEN 'Belum dianotasi'
       ELSE 'Sudah diisi; validasi belum otomatis' END, COUNT(*)
FROM m07_review_sentimen GROUP BY (sentimen IS NULL)
UNION ALL
SELECT 'Waktu kunjungan', status_waktu, COUNT(*)
FROM m07_review_waktu GROUP BY status_waktu;
COMMIT;

SELECT * FROM m07_01_rekap_sampel ORDER BY id_destinasi;
