"""
extract_pdf_corpus.py
Skrip untuk mengekstrak teks, judul, dan metadata dari seluruh file PDF di folder 'analisis rsa aes'
dan menyimpannya ke format JSON terstruktur untuk Sistem Temu Kembali Informasi (STKI).
"""

import os
import re
import json
import pymupdf

PDF_FOLDER = r"d:\smt7\STKI\analisis rsa aes"
OUTPUT_JSON = r"d:\smt7\STKI\journals.json"

def clean_text(text: str) -> str:
    """Membersihkan spasi berlebih dan karakter non-standar"""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_title_and_abstract(first_page_text: str, filename: str) -> tuple:
    """Mendeteksi judul dan cuplikan abstrak dari halaman pertama PDF"""
    lines = [l.strip() for l in first_page_text.split('\n') if l.strip()]
    
    # Ambil baris-baris yang berpotensi sebagai judul (biasanya di bagian atas setelah header jurnal)
    candidate_lines = []
    abstract_lines = []
    is_abstract = False

    for line in lines[:25]:
        lower_line = line.lower()
        if "abstrak" in lower_line or "abstract" in lower_line:
            is_abstract = True
            continue
        if is_abstract:
            abstract_lines.append(line)
        elif len(line) > 15 and not any(h in lower_line for h in ["issn", "volume", "vol.", "http", "doi", "halaman", "pages", "journal", "jurnal", "license"]):
            candidate_lines.append(line)

    title = " ".join(candidate_lines[:3]) if candidate_lines else f"Dokumen Ilmiah ({filename})"
    if len(title) > 180:
        title = title[:177] + "..."

    abstract = " ".join(abstract_lines[:10]) if abstract_lines else first_page_text[:400]
    abstract = clean_text(abstract)
    if len(abstract) > 600:
        abstract = abstract[:597] + "..."

    return title, abstract

def process_all_pdfs():
    print("==========================================================")
    print("Memulai Ekstraksi 22 Dokumen PDF dari:", PDF_FOLDER)
    print("==========================================================")

    if not os.path.exists(PDF_FOLDER):
        print(f"Error: Folder {PDF_FOLDER} tidak ditemukan!")
        return

    files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
    # Urutkan secara numerik (1.pdf, 2.pdf, ..., 22.pdf)
    files.sort(key=lambda x: int(os.path.splitext(x)[0]) if os.path.splitext(x)[0].isdigit() else 999)

    corpus = []
    
    for idx, filename in enumerate(files, start=1):
        full_path = os.path.join(PDF_FOLDER, filename)
        size_kb = round(os.path.getsize(full_path) / 1024, 1)

        try:
            doc = pymupdf.open(full_path)
            num_pages = len(doc)

            # Ekstrak halaman pertama untuk judul & abstrak
            p1_raw = doc[0].get_text()
            title, abstract = extract_title_and_abstract(p1_raw, filename)

            # Ekstrak teks halaman (batasi maksimal 20 halaman untuk efisiensi memori)
            all_text_list = []
            max_pages = min(num_pages, 20)
            for page_num in range(max_pages):
                all_text_list.append(doc[page_num].get_text())

            full_text = clean_text(" ".join(all_text_list))

            # Simpan entri korpus dokumen
            entry = {
                "id": idx,
                "filename": filename,
                "filePath": full_path,
                "title": title,
                "pageCount": num_pages,
                "sizeKb": size_kb,
                "category": "Kriptografi & Keamanan Data (RSA / AES)",
                "abstract": abstract,
                "fullText": full_text
            }

            corpus.append(entry)
            print(f"[{idx}/22] Berhasil ekstrak: {filename} ({num_pages} hal, {size_kb} KB) -> '{title[:60]}...'")

        except Exception as e:
            print(f"[{idx}/22] Gagal ekstrak {filename}: {e}")

    # Simpan ke file journals.json
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    print("\n==========================================================")
    print(f"Ekstraksi Selesai! Total {len(corpus)} dokumen disimpan ke:")
    print(OUTPUT_JSON)
    print("==========================================================")

if __name__ == "__main__":
    process_all_pdfs()
