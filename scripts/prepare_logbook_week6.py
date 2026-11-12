"""Prepare inspectable week-six documentation; no model fitting or stemming."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess,re,hashlib,sqlite3,json
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer,ENGLISH_STOP_WORDS
from openpyxl import load_workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logbook/dokumentasi/minggu_06'
COMMIT='722d07a23376e2f0407425cac22ceb469e9eb429'
def build():
 OUT.mkdir(parents=True,exist_ok=True)
 source=subprocess.check_output(['git','show',COMMIT+':src/wisata_madura/topics.py'],cwd=ROOT,text=True)
 words=re.search(r"ID_STOPWORDS = frozenset\('''(.*?)'''\.split\(\)\)",source,re.S).group(1).split()
 stop=sorted((set(words)|ENGLISH_STOP_WORDS)-{'tidak','bukan','belum','jangan','kurang','no','not','nor'})
 assert 'tidak' not in stop and 'kurang' not in stop
 pattern=r'(?u)\b[^\W\d_]{2,}\b'
 assert "token_pattern=r'"+pattern+"'" in source
 analyze=CountVectorizer(stop_words=stop,token_pattern=pattern).build_analyzer()
 raw_tokenize=CountVectorizer(token_pattern=pattern).build_analyzer()
 data_path=ROOT/'data/source/dataset_madura_bersih.xlsx';data=pd.read_excel(data_path)
 model=(data.text_preprocessed.fillna('').astype(str).str.normalize('NFKC').str.casefold().str.replace(r'[\W_]+',' ',regex=True).str.strip())
 rows=[];selected=set()
 for neg in ['tidak','kurang','bukan','belum','jangan']:
  choices=model[model.str.contains(r'\b'+neg+r'\b',regex=True)]
  for idx,text in choices.items():
   if idx in selected:continue
   selected.add(idx);tokens=analyze(text)
   assert neg in tokens
   rows.append([idx+2,str(data.loc[idx,'destinasi']),text,' | '.join(raw_tokenize(text)),' | '.join(tokens),neg,'Tetap ada pada tokenisasi sebelum penyaringan vocabulary'])
   break
 # Keep examples honest when the source contains no example for a specific word.
 control_text='Tempat ini tidak bersih dan fasilitasnya kurang terawat.'
 control_tokens=analyze(control_text)
 assert 'tidak' in control_tokens and 'kurang' in control_tokens
 control=pd.DataFrame([[control_text,' | '.join(control_tokens),'Input buatan untuk uji kontrol; bukan ulasan penelitian','tidak dan kurang tetap ada']],columns=['Input_kontrol','Token_sesudah_stopword','Asal','Hasil'])
 mono=pd.DataFrame(rows,columns=['Baris_Excel','Destinasi','Teks_model_sumber','Token_sebelum_stopword','Token_sesudah_stopword','Negasi_diperiksa','Hasil'])
 check=pd.DataFrame([[w,'Tidak' if w not in stop else 'Ya','Dipertahankan oleh aturan stopword'] for w in ['tidak','kurang','bukan','belum','jangan']],columns=['Kata','Masuk_stopword','Aturan'])
 stem=pd.DataFrame([['Status','Run v3 tidak menampilkan uji stemming baru. Belum ada tabel hasil sebelum/sesudah stemming yang dapat dijadikan bukti.'],['Bahan sumber','text_original dan text_preprocessed tersedia, tetapi perbedaan kedua kolom tidak membuktikan stemming telah diuji ulang.'],['Tindakan','Jalankan uji stemming terpisah bila tetap diperlukan; catat library, aturan, tanggal dan output aktual.'],['Hasil uji','Belum tersedia; dokumentasi belum boleh ditulis sebagai hasil pengujian selesai.']],columns=['Bagian','Keterangan'])
 dates=data[['id_destinasi','destinasi','date']].head(8).copy();dates.insert(0,'baris_excel',dates.index+2)
 dates['status_tanggal']='Relatif; bukan tanggal kunjungan absolut terverifikasi'
 dates['kebutuhan_verifikasi']='Tanggal pengambilan asli dan/atau bukti waktu kunjungan; jangan ditebak'
 context=pd.DataFrame([
 ['Kecocokan cuaca destinasi','Atribut yang tercatat pada destinasi','rekomendasi_cuaca','Kemarau; Kemarau & Penghujan','Tersedia; asal anotasi belum terverifikasi. Bukan musim kunjungan.'],
 ['Musim kunjungan','Musim ketika wisatawan benar-benar berkunjung','Waktu kunjungan absolut + lokasi + aturan musim','Belum tersedia sebagai label tervalidasi','Tidak diturunkan otomatis dari label destinasi atau ungkapan waktu relatif.'],
 ['Periode libur','Kunjungan terkait hari/periode libur tertentu','Tanggal kunjungan + kalender libur yang relevan','Belum tersedia sebagai label tervalidasi','Tidak sama dengan label cuaca. Perlu bukti waktu kunjungan.']
 ],columns=['Konsep','Makna','Sumber_yang_diperlukan','Nilai_atau_ketersediaan','Batas_pemakaian'])
 label=data.groupby('wisata').agg(jumlah_ulasan=('wisata','size'),jumlah_destinasi=('id_destinasi','nunique'),contoh_destinasi=('destinasi','first')).reset_index()
 label['status']='Label tersedia dalam sumber; contoh destinasi bukan bukti anotasi independen'
 sentiment=pd.DataFrame([
 ['Positif','Penilaian positif terhadap pengalaman/aspek yang didefinisikan','Belum dianotasi; belum menjadi target run v3'],
 ['Netral','Isi informatif tanpa kecenderungan positif/negatif menurut pedoman yang disepakati','Belum dianotasi; belum menjadi target run v3'],
 ['Negatif','Penilaian negatif terhadap pengalaman/aspek yang didefinisikan','Belum dianotasi; belum menjadi target run v3'],
 ['Campuran/ambigu','Aturan penentuan unit/aspek dan adjudikasi perlu disepakati','Rancangan pedoman; jangan dipaksa menjadi satu kelas tanpa aturan']
 ],columns=['Kategori_rancangan','Definisi_awal','Status'])
 info=pd.DataFrame([
 ['Rujukan hasil','deliverables/lda-v3/Colab_Wisata_v3_Dijalankan.ipynb; run 20261112-131554-444000'],
 ['Sumber kode tokenisasi',COMMIT+':src/wisata_madura/topics.py'],
 ['SHA256 kode rujukan',hashlib.sha256(source.encode()).hexdigest()],
 ['SHA256 workbook',hashlib.sha256(data_path.read_bytes()).hexdigest()],
 ['Waktu uji tokenisasi',datetime.now(ZoneInfo('Asia/Bangkok')).isoformat(timespec='seconds')],
 ['Batas Senin','Uji tambahan pada contoh teks model workbook; bukan output token kata yang tertanam dalam notebook. Tidak melatih atau mengubah model.'],
 ['Batas vocabulary','Kata negasi lolos aturan tokenisasi/stopword, tetapi dapat tersaring pada fitting vocabulary karena min_df/max_df/max_features.'],
 ['Status Selasa','Stemming tidak dijalankan; belum ada bukti hasil uji.'],
 ['Batas Rabu','Notebook 02 mencatat 2058 tanggal relatif; contoh di sheet Rabu berasal dari workbook aktif.'],
 ['Status Jumat','Label wisata tersedia; pedoman sentimen hanya rancangan, belum dataset sentimen tervalidasi.'],
 ['Tanggal logbook','Isi tanggal aktual kegiatan; hasil run 12 November bukan bukti pelaksanaan pada September.']
 ],columns=['Bagian','Keterangan'])
 frames={'Panduan':info,'Senin_Tokenisasi':mono,'Senin_Negasi':check,'Senin_Uji_Kontrol':control,'Selasa_Stemming':stem,'Rabu_Tanggal':dates,'Kamis_Konteks':context,'Jumat_Jenis_Wisata':label,'Jumat_Sentimen':sentiment}
 p=OUT/'Dokumentasi_Minggu_06.xlsx'
 with pd.ExcelWriter(p,engine='openpyxl') as writer:
  for name,frame in frames.items():frame.to_excel(writer,sheet_name=name,index=False)
 w=load_workbook(p)
 for s in w:
  s.freeze_panes='A2';s.auto_filter.ref=s.dimensions;s.sheet_view.showGridLines=False
  for c in s[1]:
   c.font=Font(name='Calibri',size=11,bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='194B60');c.alignment=Alignment(wrap_text=True,vertical='center')
  s.row_dimensions[1].height=32
  for row in s.iter_rows(min_row=2):
   for c in row:
    c.font=Font(name='Calibri',size=11);c.alignment=Alignment(wrap_text=True,vertical='top')
    if c.row%2==0:c.fill=PatternFill('solid',fgColor='EDF4F7')
   s.row_dimensions[row[0].row].height=90 if s.title=='Senin_Tokenisasi' else 65
  for i,c in enumerate(s[1],1):
   key=str(c.value)
   width=18 if key.startswith(('jumlah','Baris','baris','id_')) else 34
   if key in ['Keterangan','Teks_model_sumber','Token_sebelum_stopword','Token_sesudah_stopword','Definisi_awal']:width=60
   s.column_dimensions[get_column_letter(i)].width=width
  s.page_setup.orientation='landscape';s.sheet_properties.pageSetUpPr.fitToPage=True;s.page_setup.fitToWidth=1;s.page_setup.fitToHeight=0;s.print_title_rows='1:1'
 w.save(p)
 (OUT/'uji_tokenisasi.json').write_text(json.dumps({'scope':'Uji tambahan tokenisasi/stopword; bukan pelatihan ulang atau output asli notebook','source_commit':COMMIT,'source_workbook_sha256':hashlib.sha256(data_path.read_bytes()).hexdigest(),'token_pattern':pattern,'examples':rows,'controlled_input':control.to_dict(orient='records'),'stopword_checks':check.to_dict(orient='records')},ensure_ascii=False,indent=2))
 print('Workbook minggu 6 dibuat. Contoh tokenisasi aktual:',len(rows),'kategori wisata:',len(label))
if __name__=='__main__':build()
