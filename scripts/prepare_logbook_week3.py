"""Build week-3 documentation from the current workbook, without changing source data."""
from pathlib import Path
import hashlib
import sqlite3
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/source/dataset_madura_bersih.xlsx'
OUT = ROOT / 'logbook/dokumentasi/minggu_03'
COLS = ['id_destinasi','destinasi','rating','date','text_original','text_preprocessed','rekomendasi_cuaca','wisata']

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    data = pd.read_excel(SOURCE)
    if list(data.columns) != COLS:
        raise ValueError('Skema sumber berubah; periksa kamus data sebelum membuat dokumentasi.')
    stamp = datetime.now(ZoneInfo('Asia/Bangkok')).isoformat(timespec='seconds')
    fingerprint = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    normalized = lambda s: s.fillna('').astype(str).str.normalize('NFKC').str.casefold().str.replace(r'[\W_]+',' ',regex=True).str.strip()
    def blank(s):
        return s.isna() | s.fillna('').astype(str).str.strip().eq('')
    def flags(df):
        result = pd.DataFrame(index=df.index)
        for col in COLS:
            result[col+'_kosong'] = blank(df[col])
        result['rating_di_luar_1_5'] = (~blank(df.rating)) & (~pd.to_numeric(df.rating, errors='coerce').between(1,5))
        result['tanggal_relatif'] = df['date'].fillna('').astype(str).str.contains(r'\blalu\b',case=False,regex=True)
        result['duplikat_persis_tambahan'] = df.duplicated(subset=COLS,keep='first')
        keys = pd.DataFrame({'id':df.id_destinasi,'teks':normalized(df.text_preprocessed)})
        result['teks_model_kosong'] = keys.teks.eq('')
        result['teks_berulang_dalam_destinasi'] = keys.duplicated(keep='first') & keys.teks.ne('')
        result['indikasi_encoding_perlu_ditinjau'] = df.text_original.fillna('').astype(str).str.contains(r'ðŸ|â€¦|Ã©|�',case=False,regex=True)
        return result
    def audit(df):
        fl = flags(df)
        conflict = df.groupby('id_destinasi')[['destinasi','rekomendasi_cuaca','wisata']].nunique(dropna=False).gt(1).any(axis=1).sum()
        rows = [('Jumlah ulasan',len(df),'Jumlah baris yang diperiksa'),('Jumlah destinasi',df.id_destinasi.nunique(),'ID unik pada cakupan pemeriksaan')]
        for c in COLS:
            rows.append((c+' kosong',int(blank(df[c]).sum()),'Null atau teks kosong setelah trim'))
        for c in fl.columns[len(COLS):]:
            desc = 'Jumlah baris memenuhi aturan; bukan otomatis data yang harus dihapus'
            if 'duplikat' in c or 'berulang' in c:desc='Baris tambahan setelah kemunculan pertama; dihitung pada cakupan ini'
            if 'encoding' in c:desc='Pola indikatif, belum membuktikan kerusakan atau perbaikan teks'
            if 'tanggal_relatif' in c:desc='Mengandung kata lalu; bukan tanggal kunjungan absolut'
            rows.append((c,int(fl[c].sum()),desc))
        rows.append(('ID dengan nama/label tidak konsisten',int(conflict),'Satu ID memiliki lebih dari satu nama atau label'))
        return pd.DataFrame(rows,columns=['Pemeriksaan','Jumlah','Definisi'])
    # A reproducible inspection sample, not a representative or random research sample.
    sample = data.groupby('id_destinasi',sort=False,dropna=False).head(5).copy()
    sample.insert(0,'baris_excel',sample.index+2)
    dictionary = pd.DataFrame([
        ('id_ulasan','INTEGER','Primary key tambahan pada database, bukan kolom Excel','Nomor urut 1…N'),
        ('id_destinasi','INTEGER','Identitas grup destinasi; bukan unik per ulasan','19'),
        ('destinasi','TEXT','Nama destinasi dari sumber','Air Terjun Toroan'),
        ('rating','REAL','Rating dari sumber; pemeriksaan rentang 1–5','5'),
        ('date','TEXT','Nilai tanggal sumber; tidak dikonversi menjadi tanggal absolut','7 bulan lalu'),
        ('text_original','TEXT','Teks ulasan asli yang tercatat pada workbook','Lihat sampel sumber'),
        ('text_preprocessed','TEXT','Teks olahan dari sumber; bukan bukti seluruh praproses dijalankan ulang','Lihat sampel sumber'),
        ('rekomendasi_cuaca','TEXT','Label atribut destinasi; bukan musim kunjungan','Kemarau & Penghujan'),
        ('wisata','TEXT','Label kategori wisata destinasi; bukan sentimen','air terjun'),
    ],columns=['Kolom','Tipe_SQLite','Keterangan','Contoh'])
    destinations = data.groupby(['id_destinasi','destinasi'],dropna=False,sort=True).size().reset_index(name='jumlah_ulasan')
    destinations['tautan_pencarian_maps'] = destinations.destinasi.map(lambda x:'https://www.google.com/maps/search/?api=1&query='+quote(str(x)))
    destinations['kabupaten_terverifikasi'] = ''
    destinations['URL_tempat_setelah_diperiksa'] = ''
    destinations['status_verifikasi'] = 'Belum diperiksa; tautan pencarian bukan verifikasi lokasi'
    detail = data.copy();detail.insert(0,'baris_excel',data.index+2)
    fl = flags(data);detail['temuan'] = fl.apply(lambda row:'; '.join(row.index[row]),axis=1)
    detail = detail.loc[detail.temuan.ne('')]
    info = pd.DataFrame([
        ('Sumber',str(SOURCE.relative_to(ROOT))),('SHA256 sumber',fingerprint),('Waktu pemeriksaan (Asia/Bangkok)',stamp),
        ('Cakupan dataset',f'{len(data)} ulasan / {data.id_destinasi.nunique()} destinasi'),
        ('Cara memilih sampel','Lima baris pertama per ID berdasarkan urutan workbook; seluruh baris bila kurang dari lima.'),
        ('Cakupan sampel',f'{len(sample)} ulasan / {sample.id_destinasi.nunique()} destinasi'),
        ('Batas sampel','Sampel inspeksi deterministik, bukan acak atau representatif; tidak dipakai untuk skor evaluasi model.'),
        ('Audit_Sampel','Pemeriksaan dihitung hanya pada sampel; duplikat dihitung di dalam sampel.'),
        ('Audit_Dataset','Pemeriksaan atas seluruh baris workbook aktif; berbeda dari run historis v2.'),
        ('Daftar_Destinasi','Isi kabupaten dan URL tempat hanya setelah memeriksa panel lokasi di Maps.'),
        ('Tanggal dokumentasi','Gunakan waktu pemeriksaan aktual; bukan bukti pengumpulan pada minggu 3.'),
        ('Data sumber','Tidak ada baris yang dihapus, nilai yang dikoreksi, atau label yang diganti.'),
    ],columns=['Bagian','Keterangan'])
    xlsx = OUT / 'Dokumentasi_Data_Minggu_03.xlsx'
    with pd.ExcelWriter(xlsx,engine='openpyxl') as writer:
        for name,frame in [('Panduan',info),('Daftar_Destinasi',destinations),('Sampel_Ulasan',sample),('Kamus_Data',dictionary),('Audit_Sampel',audit(sample)),('Audit_Dataset',audit(data)),('Detail_Temuan',detail)]:
            frame.to_excel(writer,sheet_name=name,index=False)
    book = load_workbook(xlsx)
    for sheet in book:
        sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
        for c in sheet[1]:
            c.font=Font(name='Calibri',size=11,bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='194B60');c.alignment=Alignment(wrap_text=True,vertical='center')
        sheet.row_dimensions[1].height=32
        for row in sheet.iter_rows(min_row=2):
            for c in row:
                c.font=Font(name='Calibri',size=11);c.alignment=Alignment(wrap_text=True,vertical='top')
                if c.row%2==0:c.fill=PatternFill('solid',fgColor='EDF4F7')
        for i,col in enumerate(sheet[1],1):
            key=col.value
            width=22
            if key in ['text_original','text_preprocessed','temuan','Keterangan','Definisi']:width=55
            if key in ['tautan_pencarian_maps','URL_tempat_setelah_diperiksa','status_verifikasi']:width=40
            if key=='Pemeriksaan':width=43
            if key=='Jumlah':width=12
            sheet.column_dimensions[get_column_letter(i)].width=width
        if sheet.title in ['Sampel_Ulasan','Detail_Temuan']:
            for row in range(2,sheet.max_row+1):sheet.row_dimensions[row].height=70
        for row in sheet.iter_rows(min_row=2):
            for c in row:
                if isinstance(c.value,str) and c.value.startswith('https://'):c.hyperlink=c.value
    book.save(xlsx)
    schema = '''CREATE TABLE ulasan (
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
'''
    (OUT/'struktur_database.sql').write_text('-- Schema SQLite; id_ulasan adalah tambahan untuk primary key.\n'+schema)
    db = OUT/'dataset_wisata.sqlite'
    if db.exists():db.unlink()
    with sqlite3.connect(db) as conn:
        conn.executescript(schema)
        dbdata=data.copy();dbdata.insert(0,'id_ulasan',range(1,len(data)+1))
        dbdata.to_sql('ulasan',conn,if_exists='append',index=False)
        assert conn.execute('SELECT COUNT(*),COUNT(DISTINCT id_destinasi) FROM ulasan').fetchone()==(len(data),data.id_destinasi.nunique())
        assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    print(audit(sample).to_string(index=False))
    print('Dataset: ',len(data),'Sampel: ',len(sample),'SQLite dan XLSX terverifikasi.')

if __name__=='__main__':
    build()
