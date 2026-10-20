"""
ir_engine.py
Modul Inti Information Retrieval (STKI) Berbasis Python
Dioptimalkan untuk Temu Kembali Dokumen PDF Jurnal Kriptografi (RSA / AES / Steganografi)
"""

import math
import re
from collections import defaultdict

INDONESIAN_STOPWORDS = {
    "yang", "di", "dan", "ini", "itu", "dari", "untuk", "pada", "ke", "adalah",
    "dengan", "dalam", "sebuah", "atau", "oleh", "juga", "sebagai", "saya", "kita",
    "kami", "mereka", "anda", "dia", "ia", "akan", "telah", "bisa", "dapat",
    "ada", "saja", "karena", "jika", "maka", "tetapi", "namun", "seperti", "lebih",
    "sangat", "sekali", "tentu", "sudah", "sedang", "lagi", "pun", "serta", "jadi",
    "antara", "lalu", "kemudian", "hanya", "bagi", "sampai", "tentang", "saat",
    "agar", "supaya", "terhadap", "tanpa", "setiap", "seluruh", "semua", "banyak",
    "hasil", "dilakukan", "menunjukkan", "menggunakan", "penelitian"
}

# Kamus Sinonim Istilah Kriptografi & Keamanan Data
SYNONYMS_DICT = {
    "aes": ["simetris", "rijndael", "kriptografi", "cipher"],
    "rsa": ["asimetris", "rivest", "shamir", "adleman", "kriptografi"],
    "enkripsi": ["kriptografi", "dekripsi", "chiper", "keamanan", "encryption"],
    "dekripsi": ["enkripsi", "kriptografi", "decryption"],
    "steganografi": ["lsb", "steganography", "sisip", "citra", "gambar"],
    "citra": ["gambar", "image", "foto", "visual", "piksel"],
    "gambar": ["citra", "image", "visual"],
    "keamanan": ["security", "proteksi", "aman", "siber"],
    "siber": ["cyber", "keamanan", "security", "csirt", "bssn"],
    "hibrida": ["hybrid", "gabungan", "kombinasi"]
}

def indonesian_stemmer(word: str) -> str:
    w = word.lower()
    w = re.sub(r'(lah|kah|tah|pun)$', '', w)
    w = re.sub(r'(ku|mu|nya)$', '', w)
    w = re.sub(r'(kan|an|i)$', '', w)
    if w.startswith("meng"):
        w = w[4:]
    elif w.startswith("meny"):
        w = "s" + w[4:]
    elif w.startswith("mem"):
        w = w[3:]
    elif w.startswith("me"):
        w = w[2:]
    elif w.startswith("peng"):
        w = w[4:]
    elif w.startswith("peny"):
        w = "s" + w[4:]
    elif w.startswith("pem"):
        w = w[3:]
    elif w.startswith("pe"):
        w = w[2:]
    elif w.startswith("di"):
        w = w[2:]
    elif w.startswith("ter"):
        w = w[3:]
    elif w.startswith("ber"):
        w = w[3:]
    elif w.startswith("ke"):
        w = w[2:]
    return w

def preprocess_text(text: str, use_stemming: bool = True) -> dict:
    if not text:
        return {"original": "", "tokens": [], "filtered": [], "stemmed": [], "final": []}

    case_folded = text.lower()
    raw_tokens = re.findall(r'[a-z0-9\-]+', case_folded)
    raw_tokens = [t for t in raw_tokens if len(t) > 1 and not t.isdigit()]

    filtered_tokens = [t for t in raw_tokens if t not in INDONESIAN_STOPWORDS]

    # Jangan stem akronim dan algoritma kunci
    preserved = {"rsa", "aes", "lsb", "des", "sha", "md5", "bssn", "csirt", "jpeg", "rgb", "dct"}

    stemmed_tokens = []
    for token in filtered_tokens:
        if token in preserved or len(token) <= 3:
            stemmed_tokens.append(token)
        else:
            stemmed_tokens.append(indonesian_stemmer(token))

    return {
        "original": text,
        "case_folded": case_folded,
        "tokens": raw_tokens,
        "filtered": filtered_tokens,
        "stemmed": stemmed_tokens,
        "final": stemmed_tokens if use_stemming else filtered_tokens
    }


class InvertedIndex:
    def __init__(self, use_stemming: bool = True):
        self.use_stemming = use_stemming
        self.index = defaultdict(list)
        self.doc_lengths = {}
        self.documents = {}
        self.total_docs = 0
        self.avg_doc_length = 0.0

    def build_index(self, corpus: list):
        self.index.clear()
        self.doc_lengths.clear()
        self.documents.clear()
        self.total_docs = len(corpus)

        total_tokens = 0
        for doc in corpus:
            doc_id = doc["id"]
            self.documents[doc_id] = doc

            # Pembobotan: Judul 4x, Abstrak 2x, Fulltext 1x
            full_text = f"{doc['title']} {doc['title']} {doc['title']} {doc['title']} {doc.get('abstract', '')} {doc.get('abstract', '')} {doc.get('fullText', '')}"
            preprocessed = preprocess_text(full_text, self.use_stemming)
            tokens = preprocessed["final"]

            length = len(tokens)
            self.doc_lengths[doc_id] = length
            total_tokens += length

            tf_map = defaultdict(int)
            for t in tokens:
                tf_map[t] += 1

            for term, tf in tf_map.items():
                self.index[term].append({"doc_id": doc_id, "tf": tf})

        self.avg_doc_length = total_tokens / self.total_docs if self.total_docs > 0 else 0.0

    def get_postings(self, term: str) -> list:
        return self.index.get(term, [])

    def get_df(self, term: str) -> int:
        return len(self.get_postings(term))

    def get_vocabulary(self) -> list:
        return sorted(list(self.index.keys()))


class BM25Retriever:
    def __init__(self, inverted_index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self.inv_index = inverted_index
        self.k1 = k1
        self.b = b

    def calculate_idf(self, term: str) -> float:
        N = self.inv_index.total_docs
        df = self.inv_index.get_df(term)
        if df == 0:
            return 0.0
        return math.log(1.0 + (N - df + 0.5) / (df + 0.5))

    def search(self, query: str, enable_synonyms: bool = True, strict_and_mode: bool = False) -> dict:
        preprocessed = preprocess_text(query, self.inv_index.use_stemming)
        query_tokens = preprocessed["final"]

        if not query_tokens:
            return {"query_tokens": [], "results": []}

        concept_groups = []
        for t in query_tokens:
            group = {t}
            if enable_synonyms and t in SYNONYMS_DICT:
                group.update(SYNONYMS_DICT[t])
            concept_groups.append(list(group))

        all_effective_tokens = list(set([item for sublist in concept_groups for item in sublist]))
        expanded_tokens = [t for t in all_effective_tokens if t not in query_tokens]

        scores = defaultdict(lambda: {"score": 0.0, "matched_terms": set(), "breakdown": []})
        avgdl = self.inv_index.avg_doc_length

        for term in all_effective_tokens:
            postings = self.inv_index.get_postings(term)
            idf = self.calculate_idf(term)
            is_orig = term in query_tokens
            weight_mult = 1.0 if is_orig else 0.85

            for p in postings:
                doc_id = p["doc_id"]
                tf = p["tf"]
                doc_len = self.inv_index.doc_lengths.get(doc_id, 0)

                num = tf * (self.k1 + 1.0)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (avgdl if avgdl > 0 else 1.0)))
                term_score = idf * (num / denom) * weight_mult

                entry = scores[doc_id]
                entry["score"] += term_score
                entry["matched_terms"].add(term)
                entry["breakdown"].append({
                    "term": term,
                    "is_original": is_orig,
                    "tf": tf,
                    "idf": round(idf, 4),
                    "contribution": round(term_score, 4)
                })

        candidate_list = []
        for doc_id, data in scores.items():
            doc = self.inv_index.documents[doc_id]
            matched_terms = data["matched_terms"]

            if strict_and_mode and len(concept_groups) > 1:
                satisfies_all = all(any(term in matched_terms for term in grp) for grp in concept_groups)
                if not satisfies_all:
                    continue

            candidate_list.append({
                **doc,
                "bm25_score": round(data["score"], 4),
                "matched_terms": list(matched_terms),
                "breakdown": data["breakdown"]
            })

        ranked = sorted(candidate_list, key=lambda x: x["bm25_score"], reverse=True)

        return {
            "query_tokens": query_tokens,
            "expanded_tokens": expanded_tokens,
            "all_effective_tokens": all_effective_tokens,
            "results": ranked
        }
