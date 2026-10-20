# 🔍 JurnalSearch STKI - Sistem Temu Kembali Dokumen PDF Kriptografi (RSA & AES)

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Model](https://img.shields.io/badge/IR%20Model-Okapi%20BM25-green.svg)]()
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-orange.svg)]()
[![PDF Engine](https://img.shields.io/badge/PDF-PyMuPDF-red.svg)]()
[![Corpus](https://img.shields.io/badge/Korpus-22%20File%20PDF-purple.svg)]()

Aplikasi Desktop GUI modern untuk **Sistem Temu Kembali Informasi (STKI / Information Retrieval)** yang melakukan pencarian dan perankingan pada koleksi **22 dokumen PDF jurnal ilmiah asli** bertema kriptografi (*RSA, AES, Steganografi LSB, Keamanan Siber BSSN/CSIRT*) menggunakan algoritma **Okapi BM25** dan struktur data **Inverted Index**.

---

## 🌟 Fitur Utama Sistem

1. **Full-Text PDF Extraction (PyMuPDF)**:
   * Membaca dan mengekstrak teks langsung dari 22 file PDF di folder `analisis rsa aes/`.
   * Mengambil judul paper, jumlah halaman, ukuran file, dan teks dokumen lengkap ke dalam `journals.json`.
2. **Text Preprocessing Lengkap**:
   * *Case Folding* (mengubah teks ke huruf kecil).
   * *Tokenizing & Cleaning* (pembersihan tanda baca, angka, dan karakter non-alfabet).
   * *Stopword Removal* (membuang kata tugas umum bahasa Indonesia).
   * *Stemming* (algoritma reduksi kata berimbuhan bahasa Indonesia).
3. **Penyusunan Inverted Index**:
   * Memetakan setiap kata kunci unik (*term*) ke daftar kemunculan dokumen (*posting list*): `Term -> [{DocID, TF}]`.
   * Menghitung panjang dokumen ($|D|$) dan rata-rata panjang korpus ($\text{avgdl}$).
4. **Algoritma Pemeringkatan Okapi BM25 Berjenjang (*Field Weighting*)**:
   * Kata kunci yang cocok pada **Judul Paper** diberi bobot 4x lebih tinggi.
   * Kata kunci yang cocok pada **Abstrak** diberi bobot 2x lebih tinggi.
   * Kata kunci pada **Isi Dokumen** diberi bobot 1x.
   * Parameter: $k_1 = 1.5$ (saturasi frekuensi) dan $b = 0.75$ (penalti panjang dokumen).
5. **Solusi Perbedaan Kosakata (*Query Expansion*)**:
   * Mengatasi *vocabulary mismatch* dengan tesaurus istilah kriptografi (*AES, RSA, Steganografi, Citra, Keamanan*).
6. **Mode Mesin Pencari Konjungtif (*Strict AND Match*)**:
   * Menerapkan aturan konjungtif layaknya Google Scholar agar dokumen yang ditampilkan wajib mencakup seluruh konsep kata kunci query pengguna.
7. **Integrasi File Fisik & Windows Desktop**:
   * Tombol **Buka File PDF Asli** untuk membuka langsung dokumen sumber di PDF Viewer bawaan Windows.
   * Tombol **Rincian Skor BM25** untuk menampilkan modal transparan nilai $TF$, $IDF$, dan kontribusi skor setiap kata.

---

## 📁 Struktur Direktori Proyek

```text
jurnal-search-stki/
├── analisis rsa aes/          # Koleksi 22 file PDF jurnal ilmiah asli
│   ├── 1.pdf
│   ├── 2.pdf
│   └── ... (hingga 22.pdf)
├── dist/                      # File aplikasi executable siap pakai
│   └── JurnalSearch_PDF.exe   # Aplikasi Windows (.EXE) mandiri (~32 MB)
├── app.py                     # Antarmuka Desktop GUI (CustomTkinter)
├── ir_engine.py               # Engine STKI (Inverted Index, BM25, Preprocessing)
├── extract_pdf_corpus.py      # Ekstraktor teks PDF ke korpus JSON
├── journals.json              # Korpus metadata & teks hasil ekstraksi 22 PDF
├── requirements.txt           # Daftar pustaka Python yang dibutuhkan
├── build_exe.bat              # Skrip kompilasi otomatis ke file .EXE
└── README.md                  # Dokumentasi teknis proyek
```

---

## 🚀 Cara Menjalankan Aplikasi

### Opsi 1: Menjalankan File Executable (.EXE) Siap Pakai (Rekomendasi)
Anda dapat langsung menjalankan aplikasi tanpa perlu instalasi lingkungan Python:
1. Masuk ke folder `dist/`.
2. Klik ganda file: **`JurnalSearch_PDF.exe`**.

### Opsi 2: Menjalankan via Source Code Python
1. Pastikan **Python 3.10+** sudah terpasang.
2. Clone repositori ini:
   ```bash
   git clone https://github.com/DerandaBagas17/jurnal-search-stki.git
   cd jurnal-search-stki
   ```
3. Instal pustaka yang dibutuhkan:
   ```bash
   pip install -r requirements.txt
   ```
   *(atau `pip install customtkinter pymupdf`)*
4. Jalankan aplikasi:
   ```bash
   python app.py
   ```

---

## 📐 Formula Matematis Okapi BM25

Skor relevansi dokumen $D$ terhadap query $Q$ dihitung menggunakan formula Robertson-Spärck Jones Okapi BM25:

$$\text{Score}(D, Q) = \sum_{q \in Q} \text{IDF}(q) \times \frac{\text{TF}(q, D) \times (k_1 + 1)}{\text{TF}(q, D) + k_1 \times \left(1 - b + b \times \frac{|D|}{\text{avgdl}}\right)}$$

Di mana nilai **Inverse Document Frequency (IDF)** dihitung dengan formula non-negatif:

$$\text{IDF}(q) = \ln\left(1 + \frac{N - \text{df}(q) + 0.5}{\text{df}(q) + 0.5}\right)$$

* $N$ = Total dokumen dalam korpus (22 dokumen).
* $\text{df}(q)$ = Jumlah dokumen yang memuat kata kunci $q$.
* $\text{TF}(q, D)$ = Frekuensi kemunculan kata $q$ di dalam dokumen $D$ (dengan field weighting).
* $|D|$ = Jumlah total token kata dalam dokumen $D$.
* $\text{avgdl}$ = Rata-rata jumlah token kata di seluruh dokumen korpus.

---

## 🛠️ Kompilasi Ulang ke File .EXE

Jika terdapat pembaruan file PDF atau kode engine:
1. Ekstrak ulang data teks:
   ```bash
   python extract_pdf_corpus.py
   ```
2. Kompilasi ulang ke file `.exe`:
   * Klik ganda file **`build_exe.bat`**, atau
   * Jalankan perintah PyInstaller:
     ```bash
     python -m PyInstaller --noconsole --onefile --name "JurnalSearch_PDF" --add-data "journals.json;." --collect-all customtkinter app.py
     ```

---

## 👤 Penulis
* **Nama:** Deranda Bagas Pamungkas
* **Repositori:** [github.com/DerandaBagas17/jurnal-search-stki](https://github.com/DerandaBagas17/jurnal-search-stki)
* **Mata Kuliah:** Sistem Temu Kembali Informasi (STKI)
* **Program Studi:** Teknik Informatika
