# 🔍 JurnalSearch STKI - Sistem Temu Kembali Informasi Dokumen Jurnal Ilmiah (Okapi BM25 & Inverted Index)

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Model](https://img.shields.io/badge/IR%20Model-Okapi%20BM25-green.svg)]()
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-orange.svg)]()
[![PDF Engine](https://img.shields.io/badge/PDF-PyMuPDF-red.svg)]()
[![Corpus](https://img.shields.io/badge/Korpus-Dokumen%20Jurnal%20PDF-purple.svg)]()

Aplikasi Desktop GUI modern untuk **Sistem Temu Kembali Informasi (STKI / Information Retrieval)** yang melakukan pencarian, ekstraksi teks otomatis, dan pemeringkatan relevansi pada repositori **dokumen PDF artikel jurnal ilmiah** menggunakan algoritma probabilistik **Okapi BM25** dan struktur data **Inverted Index**. 

Sistem didesain modular dan fleksibel sehingga dapat digunakan untuk mencari berbagai jenis koleksi dokumen jurnal ilmiah (multi-topik / umum) secara cepat dan akurat, lengkap dengan pembuka dokumen fisik PDF asli.

---

## 🌟 Fitur Utama Sistem

1. **Full-Text PDF Extraction (PyMuPDF / fitz)**:
   * Membaca dan mengekstrak teks serta metadata langsung dari berkas fisik PDF di folder korpus.
   * Menyimpan judul paper, jumlah halaman, ukuran berkas, dan isi teks lengkap ke dalam korpus terstruktur `journals.json`.
2. **Text Preprocessing Pipeline Lengkap**:
   * *Case Folding* (standarisasi teks menjadi huruf kecil).
   * *Tokenizing & Cleaning* (pembersihan tanda baca khusus, angka, dan karakter non-alfabet).
   * *Stopword Removal* (penghapusan kata-kata umum yang tidak bermakna informasi).
   * *Stemming* (reduksi kata berimbuhan ke bentuk kata dasar).
3. **Penyusunan Inverted Index**:
   * Memetakan setiap kata kunci unik (*term*) ke daftar kemunculan dokumen (*posting list*): `Term -> [{DocID, TF}]`.
   * Menghitung panjang dokumen ($|D|$) dan rata-rata panjang korpus ($\text{avgdl}$).
4. **Algoritma Pemeringkatan Okapi BM25 Berjenjang (*Field Weighting*)**:
   * Kata kunci yang cocok pada **Judul Paper** diberi prioritas bobot lebih tinggi (4x).
   * Kata kunci yang cocok pada **Abstrak** diberi bobot 2x.
   * Kata kunci pada **Isi Dokumen** diberi bobot standar (1x).
   * Parameter standar: $k_1 = 1.5$ (faktor saturasi frekuensi term) dan $b = 0.75$ (faktor penalti panjang dokumen).
5. **Solusi Perbedaan Kosakata (*Query Expansion*)**:
   * Mengatasi permasalahan *vocabulary mismatch* dengan mekanisme tesaurus istilah terkait untuk memperkaya kata kunci kueri pencarian pengguna.
6. **Mode Mesin Pencari Konjungtif (*Strict AND Match*)**:
   * Menerapkan aturan konjungtif layaknya Google Scholar agar dokumen yang ditampilkan wajib mencakup seluruh konsep kata kunci query pengguna.
7. **Integrasi File Fisik & Windows Desktop**:
   * Tombol **Buka File PDF Asli** untuk membuka langsung dokumen sumber di PDF Viewer bawaan Windows.
   * Tombol **Rincian Skor BM25** untuk menampilkan modal transparan nilai $TF$, $IDF$, dan kontribusi skor setiap kata.

---

## 📁 Struktur Direktori Proyek

```text
jurnal-search-stki/
├── analisis rsa aes/          # Koleksi dokumen PDF jurnal ilmiah asli
│   ├── 1.pdf
│   ├── 2.pdf
│   └── ...
├── dist/                      # File aplikasi executable siap pakai
│   └── JurnalSearch_PDF.exe   # Aplikasi Windows (.EXE) mandiri (~32 MB)
├── app.py                     # Antarmuka Desktop GUI (CustomTkinter)
├── ir_engine.py               # Engine STKI (Inverted Index, BM25, Preprocessing)
├── extract_pdf_corpus.py      # Ekstraktor teks dokumen PDF ke korpus JSON
├── journals.json              # Korpus metadata & teks hasil ekstraksi PDF
├── requirements.txt           # Daftar dependensi pustaka Python
├── build_exe.bat              # Skrip kompilasi otomatis ke file .EXE
└── README.md                  # Dokumentasi teknis proyek
```

---

## 🚀 Cara Menjalankan Aplikasi

### Opsi 1: Menjalankan File Executable (.EXE) Siap Pakai (Rekomendasi)
Anda dapat langsung menjalankan aplikasi tanpa perlu konfigurasi lingkungan Python:
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

* $N$ = Total dokumen dalam korpus.
* $\text{df}(q)$ = Jumlah dokumen yang memuat kata kunci $q$.
* $\text{TF}(q, D)$ = Frekuensi kemunculan kata $q$ di dalam dokumen $D$ (dengan field weighting).
* $|D|$ = Jumlah total token kata dalam dokumen $D$.
* $\text{avgdl}$ = Rata-rata jumlah token kata di seluruh dokumen korpus.

---

## 🛠️ Menambahkan Dokumen PDF Baru & Kompilasi Ulang

Jika Anda ingin mengganti atau menambahkan dokumen PDF jurnal ilmiah baru:
1. Masukkan file PDF baru ke dalam folder dokumen.
2. Jalankan ekstraktor teks otomatis:
   ```bash
   python extract_pdf_corpus.py
   ```
3. Jalankan kembali `python app.py` atau kompilasi ulang file executable dengan:
   * Menjalankan **`build_exe.bat`**, atau
   * Menjalankan perintah PyInstaller:
     ```bash
     python -m PyInstaller --noconsole --onefile --name "JurnalSearch_PDF" --add-data "journals.json;." --collect-all customtkinter app.py
     ```

---

## 👤 Informasi Mahasiswa
* **Nama Lengkap:** Deranda Bagas Pamungkas
* **NIM:** A11.2023.14906
* **Mata Kuliah:** Sistem Temu Kembali Informasi (STKI)
* **Program Studi:** Teknik Informatika
* **Repositori GitHub:** [https://github.com/DerandaBagas17/jurnal-search-stki](https://github.com/DerandaBagas17/jurnal-search-stki)
