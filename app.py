"""
app.py
Aplikasi Desktop Sistem Temu Kembali Dokumen PDF Jurnal Kriptografi (RSA & AES)
Dibangun menggunakan Python & CustomTkinter (Dapat Dikompilasi Menjadi .EXE)
"""

import os
import sys
import json
import customtkinter as ctk
from ir_engine import InvertedIndex, BM25Retriever, preprocess_text

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JurnalPDFSearchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("JurnalSearch STKI - Sistem Temu Kembali 22 Dokumen PDF (RSA & AES)")
        self.geometry("1200x840")
        self.minsize(980, 720)

        self.load_data()
        self.rebuild_engine()
        self.create_widgets()

        # Jalankan pencarian default
        self.search_entry.insert(0, "enkripsi aes steganografi lsb")
        self.execute_search()

    def load_data(self):
        json_path = get_resource_path("journals.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self.journals = json.load(f)
        except Exception as e:
            print(f"Error memuat journals.json: {e}")
            self.journals = []

    def rebuild_engine(self):
        use_stemming = getattr(self, "stemming_var", None)
        use_stem = use_stemming.get() if use_stemming is not None else True
        
        self.inv_index = InvertedIndex(use_stemming=use_stem)
        self.inv_index.build_index(self.journals)

        k1_val = getattr(self, "k1_slider", None)
        k1 = k1_val.get() if k1_val is not None else 1.5
        b_val = getattr(self, "b_slider", None)
        b = b_val.get() if b_val is not None else 0.75

        self.bm25 = BM25Retriever(self.inv_index, k1=k1, b=b)

    def create_widgets(self):
        # 1. Header Frame
        header_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=("#1A2234", "#111827"))
        header_frame.pack(fill="x", padx=18, pady=(16, 10))

        title_label = ctk.CTkLabel(
            header_frame, 
            text="📑 PDF Search STKI (RSA & AES)", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=14)

        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="Temu Kembali 22 Dokumen PDF Jurnal Kriptografi • Okapi BM25 • Inverted Index", 
            font=ctk.CTkFont(size=12),
            text_color="#9CA3AF"
        )
        subtitle_label.pack(side="left", padx=10, pady=14)

        stats_badge = ctk.CTkLabel(
            header_frame,
            text=f"Total: {len(self.journals)} PDF | {len(self.inv_index.get_vocabulary())} Kosakata",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#0F3E6D", "#1E3A8A"),
            corner_radius=8,
            padx=12,
            pady=4
        )
        stats_badge.pack(side="right", padx=20, pady=14)

        # 2. Search & Controls Frame
        search_card = ctk.CTkFrame(self, corner_radius=12, fg_color=("#1F293D", "#161F30"))
        search_card.pack(fill="x", padx=18, pady=6)

        search_input_row = ctk.CTkFrame(search_card, fg_color="transparent")
        search_input_row.pack(fill="x", padx=16, pady=(14, 8))

        self.search_entry = ctk.CTkEntry(
            search_input_row, 
            placeholder_text="Ketik kata kunci, misal: enkripsi aes, steganografi lsb, rsa asimetris, keamanan siber...",
            font=ctk.CTkFont(size=14),
            height=42
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.execute_search())

        search_btn = ctk.CTkButton(
            search_input_row, 
            text="🔍 Cari Dokumen", 
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42,
            width=150,
            command=self.execute_search
        )
        search_btn.pack(side="right")

        # Chips Contoh Query
        chips_row = ctk.CTkFrame(search_card, fg_color="transparent")
        chips_row.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(chips_row, text="Uji Coba Query:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#9CA3AF").pack(side="left", padx=(0, 8))

        sample_queries = [
            ("Steganografi LSB", "enkripsi aes steganografi lsb"),
            ("Komparasi RSA & AES", "studi komparatif kriptografi rsa dan aes"),
            ("Keamanan Siber BSSN", "laporan lanskap keamanan siber bssn"),
            ("Hybrid Encryption", "rsa aes hybrid encryption cloud"),
            ("Enkripsi Citra Gambar", "kriptografi citra digital gambar")
        ]

        for label, q in sample_queries:
            btn = ctk.CTkButton(
                chips_row,
                text=label,
                font=ctk.CTkFont(size=11),
                height=26,
                fg_color=("#2C3B59", "#243049"),
                hover_color=("#3B82F6", "#2563EB"),
                command=lambda val=q: self.fill_and_search(val)
            )
            btn.pack(side="left", padx=4)

        # Opsi Filter
        controls_row = ctk.CTkFrame(search_card, fg_color="transparent")
        controls_row.pack(fill="x", padx=16, pady=(4, 12))

        self.stemming_var = ctk.BooleanVar(value=True)
        stem_chk = ctk.CTkCheckBox(
            controls_row, text="Stemming Bahasa Indonesia", 
            variable=self.stemming_var, font=ctk.CTkFont(size=12),
            command=self.on_param_change
        )
        stem_chk.pack(side="left", padx=(0, 16))

        self.synonym_var = ctk.BooleanVar(value=True)
        syn_chk = ctk.CTkCheckBox(
            controls_row, text="Query Expansion (Sinonim Kriptografi)", 
            variable=self.synonym_var, font=ctk.CTkFont(size=12),
            command=self.execute_search
        )
        syn_chk.pack(side="left", padx=(0, 16))

        self.strict_and_var = ctk.BooleanVar(value=True)
        strict_chk = ctk.CTkCheckBox(
            controls_row, text="Mode Mesin Pencari (Wajib Cocok Semua Kata)", 
            variable=self.strict_and_var, font=ctk.CTkFont(size=12),
            command=self.execute_search
        )
        strict_chk.pack(side="left", padx=(0, 16))

        # 3. Tabview Navigasi
        self.tabview = ctk.CTkTabview(self, corner_radius=12)
        self.tabview.pack(fill="both", expand=True, padx=18, pady=(4, 16))

        self.tab_results = self.tabview.add("🔍 Hasil Pencarian Dokumen")
        self.tab_corpus = self.tabview.add("📚 Daftar 22 File PDF Korpus")
        self.tab_index = self.tabview.add("🗂️ Inverted Index")
        self.tab_concept = self.tabview.add("🧠 Alur Ekstraksi PDF & BM25")

        self.results_scroll = ctk.CTkScrollableFrame(self.tab_results, fg_color="transparent")
        self.results_scroll.pack(fill="both", expand=True, padx=4, pady=4)

        self.setup_corpus_tab()
        self.setup_index_tab()
        self.setup_concept_tab()

    def fill_and_search(self, query):
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, query)
        self.execute_search()

    def on_param_change(self):
        self.rebuild_engine()
        self.execute_search()
        self.setup_index_tab()

    def execute_search(self):
        query = self.search_entry.get().strip()
        if not query:
            return

        enable_syn = self.synonym_var.get()
        strict_mode = self.strict_and_var.get()

        search_res = self.bm25.search(
            query, 
            enable_synonyms=enable_syn, 
            strict_and_mode=strict_mode
        )
        
        results = search_res["results"]
        query_tokens = search_res["query_tokens"]
        effective_tokens = search_res.get("all_effective_tokens", query_tokens)

        for widget in self.results_scroll.winfo_children():
            widget.destroy()

        mode_label = "Mode Mesin Pencari (AND) Aktif" if strict_mode else "Mode Bebas (OR)"
        header_lbl = ctk.CTkLabel(
            self.results_scroll,
            text=f"Ditemukan {len(results)} Dokumen PDF Relevan ({mode_label})",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        )
        header_lbl.pack(fill="x", padx=6, pady=(4, 10))

        if not results:
            empty_box = ctk.CTkFrame(self.results_scroll, corner_radius=10, fg_color="#182234")
            empty_box.pack(fill="x", padx=10, pady=20)
            ctk.CTkLabel(
                empty_box, 
                text="❌ Tidak Ada Dokumen PDF yang Cocok\nCoba nonaktifkan 'Mode Mesin Pencari' atau gunakan kata kunci umum seperti 'rsa', 'aes', 'steganografi'.",
                font=ctk.CTkFont(size=14),
                pady=30
            ).pack()
            return

        for idx, doc in enumerate(results):
            self.render_pdf_card(idx + 1, doc, effective_tokens)

    def render_pdf_card(self, rank, doc, query_tokens):
        card = ctk.CTkFrame(self.results_scroll, corner_radius=10, fg_color=("#1C263A", "#151E2E"))
        card.pack(fill="x", padx=4, pady=6)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(12, 4))

        pdf_badge = ctk.CTkLabel(
            top_row,
            text=f"📄 {doc.get('filename')} • {doc.get('pageCount', 0)} Hal • {doc.get('sizeKb', 0)} KB",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#065F46",
            text_color="#A7F3D0",
            corner_radius=6,
            padx=10,
            pady=3
        )
        pdf_badge.pack(side="left")

        score_badge = ctk.CTkLabel(
            top_row,
            text=f"Skor BM25: {doc['bm25_score']}",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#1E3A8A",
            text_color="#93C5FD",
            corner_radius=6,
            padx=10,
            pady=3
        )
        score_badge.pack(side="right")

        # Judul Paper
        title_lbl = ctk.CTkLabel(
            card,
            text=f"{rank}. {doc['title']}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#FFFFFF",
            wraplength=950,
            justify="left",
            anchor="w"
        )
        title_lbl.pack(fill="x", padx=16, pady=(4, 2))

        # Cuplikan Abstrak
        abstract_lbl = ctk.CTkLabel(
            card,
            text=f'"{doc.get("abstract", "")}"',
            font=ctk.CTkFont(size=12),
            text_color="#D1D5DB",
            wraplength=950,
            justify="left",
            anchor="w"
        )
        abstract_lbl.pack(fill="x", padx=16, pady=(0, 8))

        # Baris Aksi
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(4, 12))

        matched_str = ", ".join(doc.get("matched_terms", []))
        ctk.CTkLabel(
            btn_row, 
            text=f"Kata Kunci Cocok: {matched_str}", 
            font=ctk.CTkFont(size=11), 
            text_color="#FBBF24"
        ).pack(side="left")

        actions_group = ctk.CTkFrame(btn_row, fg_color="transparent")
        actions_group.pack(side="right")

        # Tombol Buka File PDF Asli
        open_pdf_btn = ctk.CTkButton(
            actions_group,
            text="📑 Buka File PDF Asli",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=30,
            command=lambda path=doc.get("filePath"): self.open_pdf_file(path)
        )
        open_pdf_btn.pack(side="left", padx=(0, 8))

        # Tombol Rincian BM25
        calc_btn = ctk.CTkButton(
            actions_group,
            text="📊 Rincian Skor BM25",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=30,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=lambda d=doc: self.show_bm25_details(d)
        )
        calc_btn.pack(side="left")

    def open_pdf_file(self, file_path):
        """Membuka file PDF menggunakan viewer bawaan Windows"""
        if file_path and os.path.exists(file_path):
            try:
                os.startfile(file_path)
            except Exception as e:
                print(f"Error membuka PDF: {e}")
        else:
            print(f"File PDF tidak ditemukan: {file_path}")

    def show_bm25_details(self, doc):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Rincian Okapi BM25 - {doc['filename']}")
        popup.geometry("660x460")
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text=f"Rincian Skor BM25: {doc['filename']} - {doc['title'][:70]}...",
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=620
        ).pack(padx=16, pady=(16, 8))

        info_lbl = ctk.CTkLabel(
            popup,
            text=f"Total Skor BM25: {doc['bm25_score']} | Parameter: k1=1.5, b=0.75",
            font=ctk.CTkFont(size=12),
            text_color="#38BDF8"
        )
        info_lbl.pack(padx=16, pady=(0, 12))

        scroll = ctk.CTkScrollableFrame(popup)
        scroll.pack(fill="both", expand=True, padx=16, pady=10)

        header = ctk.CTkFrame(scroll, fg_color="#1E293B")
        header.pack(fill="x", pady=2)
        ctk.CTkLabel(header, text="Term (Kata)", width=140, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=6)
        ctk.CTkLabel(header, text="TF", width=60, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=4)
        ctk.CTkLabel(header, text="IDF", width=80, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=4)
        ctk.CTkLabel(header, text="Tipe", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=4)
        ctk.CTkLabel(header, text="Kontribusi", width=100, anchor="e", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10)

        for b in doc["breakdown"]:
            row = ctk.CTkFrame(scroll, fg_color="#111827")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=b["term"], width=140, anchor="w", text_color="#38BDF8").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=str(b["tf"]), width=60).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=str(b["idf"]), width=80).pack(side="left", padx=4)
            tipe = "Asli" if b.get("is_original", True) else "Sinonim"
            ctk.CTkLabel(row, text=tipe, width=100, text_color="#34D399" if tipe=="Sinonim" else "#E5E7EB").pack(side="left", padx=4)
            ctk.CTkLabel(row, text=f"+{b['contribution']}", width=100, anchor="e", text_color="#FBBF24", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10)

    def setup_corpus_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_corpus)
        scroll.pack(fill="both", expand=True, padx=6, pady=6)

        ctk.CTkLabel(
            scroll, 
            text=f"Daftar Seluruh Korpus ({len(self.journals)} Dokumen PDF)", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(6, 12))

        for j in self.journals:
            box = ctk.CTkFrame(scroll, corner_radius=8, fg_color="#151E2E")
            box.pack(fill="x", padx=6, pady=6)

            top = ctk.CTkFrame(box, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(10, 4))

            ctk.CTkLabel(
                top, 
                text=f"📄 {j['filename']} - {j['title']}", 
                font=ctk.CTkFont(size=13, weight="bold"), 
                text_color="#38BDF8",
                anchor="w",
                wraplength=750
            ).pack(side="left")

            open_btn = ctk.CTkButton(
                top,
                text="Buka PDF",
                width=80,
                height=26,
                fg_color="#059669",
                command=lambda p=j.get('filePath'): self.open_pdf_file(p)
            )
            open_btn.pack(side="right")

            ctk.CTkLabel(
                box, 
                text=f"Ukuran: {j.get('sizeKb')} KB | Jumlah Halaman: {j.get('pageCount')} Hal", 
                font=ctk.CTkFont(size=11), 
                text_color="#9CA3AF",
                anchor="w"
            ).pack(fill="x", padx=12, pady=(0, 6))

            ctk.CTkLabel(
                box, 
                text=j.get('abstract', '')[:300] + "...", 
                font=ctk.CTkFont(size=12), 
                wraplength=900,
                justify="left"
            ).pack(fill="x", padx=12, pady=(0, 10))

    def setup_index_tab(self):
        for widget in self.tab_index.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.tab_index)
        scroll.pack(fill="both", expand=True, padx=6, pady=6)

        vocab = self.inv_index.get_vocabulary()
        ctk.CTkLabel(
            scroll, 
            text=f"Inverted Index dari 22 File PDF ({len(vocab)} Kosakata Unik)", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(6, 12))

        h = ctk.CTkFrame(scroll, fg_color="#1E293B")
        h.pack(fill="x", pady=2)
        ctk.CTkLabel(h, text="Term", width=140, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=8)
        ctk.CTkLabel(h, text="DF", width=50, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=6)
        ctk.CTkLabel(h, text="IDF", width=70, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=6)
        ctk.CTkLabel(h, text="Posting List [Doc ID, TF]", anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", fill="x", expand=True, padx=8)

        # Tampilkan 150 kata teratas
        for term in vocab[:150]:
            postings = self.inv_index.get_postings(term)
            df = len(postings)
            idf = round(self.bm25.calculate_idf(term), 4)
            post_str = " ".join([f"[{p['doc_id']}.pdf, TF:{p['tf']}]" for p in postings[:8]])
            if len(postings) > 8:
                post_str += " ..."

            row = ctk.CTkFrame(scroll, fg_color="#111827")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=term, width=140, anchor="w", text_color="#38BDF8").pack(side="left", padx=8)
            ctk.CTkLabel(row, text=str(df), width=50).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=str(idf), width=70).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=post_str, anchor="w", text_color="#D1D5DB").pack(side="left", fill="x", expand=True, padx=8)

    def setup_concept_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_concept)
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(
            scroll, 
            text="Alur Ekstraksi PDF & Pemeringkatan Okapi BM25", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#38BDF8"
        ).pack(anchor="w", pady=(6, 12))

        desc = (
            "1. Ekstraksi Dokumen PDF Asli:\n"
            "   • Sebanyak 22 file PDF di folder 'analisis rsa aes' diekstrak menggunakan library PyMuPDF.\n"
            "   • Judul paper, jumlah halaman, dan teks lengkap diparsing ke dalam korpus data.\n\n"
            "2. Text Preprocessing:\n"
            "   • Case Folding: Mengubah seluruh teks menjadi huruf kecil.\n"
            "   • Tokenizing: Memotong teks menjadi token kata dan membuang karakter non-alfabet.\n"
            "   • Stopword Removal: Membuang kata hubung bahasa Indonesia.\n"
            "   • Stemming Nazief & Adriani: Menyeragamkan kata berimbuhan menjadi kata dasar.\n\n"
            "3. Pembobotan Berjenjang (Field Weighting):\n"
            "   • Judul Paper diberi bobot 4x lebih tinggi.\n"
            "   • Abstrak diberi bobot 2x lebih tinggi.\n"
            "   • Teks Isi Dokumen diberi bobot 1x.\n\n"
            "4. Formula Okapi BM25:\n"
            "   Score(D, Q) = ∑ IDF(q_i) × [ TF × (k1 + 1) ] / [ TF + k1 × (1 - b + b × (|D| / avgdl)) ]\n"
            "   • k1 = 1.5 (Saturasi Frekuensi Kata)\n"
            "   • b = 0.75 (Penalti Panjang Halaman Dokumen PDF)\n\n"
            "5. Aksi Langsung:\n"
            "   • Klik tombol 'Buka File PDF Asli' untuk membaca langsung file sumber di Windows."
        )

        ctk.CTkLabel(
            scroll, 
            text=desc, 
            font=ctk.CTkFont(size=13),
            justify="left",
            anchor="w"
        ).pack(fill="x", padx=10, pady=8)


if __name__ == "__main__":
    app = JurnalPDFSearchApp()
    app.mainloop()
