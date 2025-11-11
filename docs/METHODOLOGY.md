# 📖 Dokumentasi Metodologi Penelitian

## Deteksi Plagiarisme Semantik Menggunakan Google CSE dan Sentence-BERT

---

## 1. Pendahuluan

### 1.1 Latar Belakang Masalah

Plagiarisme merupakan masalah serius dalam dunia akademik. Plagiarisme semantik, dimana mahasiswa melakukan parafrase (menulis ulang dengan kata-kata berbeda namun makna sama) sangat sulit dideteksi menggunakan sistem deteksi plagiarisme konvensional yang hanya mencocokkan kata per kata (literal matching).

**Masalah:**
- Deteksi plagiarisme literal tidak efektif untuk parafrase
- Mahasiswa sering mengubah struktur kalimat untuk menghindari deteksi
- Fakultas Teknik UNISMUH Makassar belum memiliki sistem deteksi berbasis makna

**Solusi:**
- Menggunakan Sentence-BERT untuk analisis kemiripan semantik
- Integrasi Google CSE untuk pencarian referensi otomatis
- Deteksi berdasarkan makna, bukan hanya kata

---

## 2. Metodologi Penelitian

### 2.1 Jenis Penelitian

Penelitian ini merupakan **penelitian terapan (applied research)** dengan metode **Research and Development (R&D)** yang menghasilkan produk berupa sistem deteksi plagiarisme semantik.

### 2.2 Tahapan Penelitian

```
┌─────────────────────────────────────────────────────────────┐
│  1. Studi Literatur                                        │
│     - Review paper tentang plagiarisme semantik            │
│     - Studi tentang Sentence-BERT dan transformers         │
│     - Analisis sistem deteksi plagiarisme existing         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Analisis Kebutuhan                                     │
│     - Identifikasi kebutuhan sistem                        │
│     - Analisis dataset (abstrak skripsi)                   │
│     - Definisi requirement fungsional & non-fungsional     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Desain Sistem                                          │
│     - Arsitektur sistem                                    │
│     - Desain algoritma deteksi                             │
│     - Desain database dan API                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Implementasi                                           │
│     - Implementasi backend (Python/FastAPI)                │
│     - Implementasi frontend (React)                        │
│     - Integrasi Google CSE dan SBERT                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  5. Testing & Evaluasi                                     │
│     - Unit testing                                         │
│     - Functional testing                                   │
│     - Performance testing                                  │
│     - Evaluasi akurasi dengan confusion matrix             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  6. Dokumentasi & Deployment                               │
│     - Dokumentasi sistem                                   │
│     - Deployment ke server                                 │
│     - Sosialisasi ke pengguna                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Algoritma Deteksi Plagiarisme

### 3.1 Flowchart Sistem

```
        [START]
           ↓
    [Input PDF File]
           ↓
    [Extract Text]
   (PyPDF2/pdfplumber)
           ↓
  [Preprocessing Text]
  - Remove whitespace
  - Clean characters
           ↓
  [Text Segmentation]
  Sliding Window:
  - Size: 25 words
  - Overlap: 5 words
           ↓
    ┌─────────┐
    │ For each│
    │ segment │
    └─────────┘
           ↓
  [Search Google CSE]
  - Query: segment text
  - Get top 5 snippets
           ↓
[Calculate Similarity]
   using SBERT:
   - Encode segment
   - Encode snippets
   - Cosine similarity
           ↓
     [Classify]
   similarity >= threshold?
    ↙            ↘
  YES            NO
   ↓              ↓
[Plagiat]    [Original]
   ↓              ↓
    └──────┬──────┘
           ↓
  [Generate Report]
  - Statistics
  - Details per segment
  - CSV export
           ↓
        [END]
```

### 3.2 Pseudocode Utama

```python
FUNCTION detect_plagiarism(text):
    # 1. Preprocessing
    cleaned_text = preprocess(text)
    
    # 2. Segmentation
    segments = sliding_window(cleaned_text, size=25, overlap=5)
    
    # 3. Detection per segment
    results = []
    FOR each segment IN segments:
        # Search references
        snippets = google_search(segment.text, num_results=5)
        
        # Calculate similarity
        max_similarity = 0
        best_match = None
        
        FOR each snippet IN snippets:
            similarity = cosine_similarity(
                sbert_encode(segment.text),
                sbert_encode(snippet)
            )
            
            IF similarity > max_similarity:
                max_similarity = similarity
                best_match = snippet
        
        # Classify
        IF max_similarity >= threshold:
            label = "Plagiat"
        ELSE:
            label = "Original"
        
        results.append({
            segment_id: segment.id,
            text: segment.text,
            similarity: max_similarity,
            label: label,
            source: best_match.url
        })
    
    # 4. Generate statistics
    plagiarism_percentage = (count(Plagiat) / total_segments) * 100
    
    RETURN {
        total_segments: len(segments),
        plagiarized: count(Plagiat),
        percentage: plagiarism_percentage,
        details: results
    }
END FUNCTION
```

---

## 4. Teknik dan Metode

### 4.1 Sliding Window Technique

**Konsep:**
Memotong teks menjadi segmen-segmen kecil dengan overlap untuk memastikan tidak ada kalimat penting yang terlewat.

**Parameter:**
- **Window Size**: 25 kata (±1 paragraf kecil)
- **Overlap**: 5 kata (20% dari window size)

**Contoh:**
```
Text: "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z"
      [─────────Window 1─────────] (A-Y)
           [─────────Window 2─────────] (F-Z)
```

**Rumus:**
```
next_position = current_position + (window_size - overlap)
total_windows = ceil((text_length - window_size) / (window_size - overlap)) + 1
```

### 4.2 Sentence-BERT (SBERT)

**Model:** `paraphrase-multilingual-mpnet-base-v2`

**Karakteristik:**
- Mendukung 50+ bahasa (termasuk Indonesia & Inggris)
- Menghasilkan sentence embeddings 768-dimensional
- Pre-trained untuk paraphrase identification

**Proses Encoding:**
```python
# Input: "Penelitian ini bertujuan untuk..."
text → Tokenization → BERT Layers → Pooling → Embedding Vector (768-dim)
```

**Keunggulan:**
- Memahami konteks kalimat, bukan hanya kata
- Dapat mendeteksi sinonim dan parafrase
- Lebih cepat dari model BERT tradisional

### 4.3 Cosine Similarity

**Formula:**
```
                    A · B
similarity = ─────────────────
             ||A|| × ||B||

Dimana:
- A, B = Vector embeddings
- A · B = Dot product
- ||A||, ||B|| = Magnitude vectors
```

**Interpretasi:**
- 0.90 - 1.00: Sangat mirip (kemungkinan plagiat tinggi)
- 0.75 - 0.89: Mirip (perlu review)
- 0.60 - 0.74: Cukup mirip (borderline)
- < 0.60: Tidak mirip (original)

**Threshold Default:** 0.75 (dapat disesuaikan)

---

## 5. Objek dan Sampel Penelitian

### 5.1 Objek Penelitian

**Target:** Abstrak skripsi mahasiswa Teknik Informatika UNISMUH Makassar

**Karakteristik:**
- Bahasa: Indonesia dan/atau Inggris
- Panjang: 150-300 kata
- Format: PDF
- Periode: Tahun 2020-2024

### 5.2 Sampel Data

**Training/Testing Set:**
- **Total**: 100 abstrak skripsi
- **Plagiat** (30%): 30 abstrak dengan parafrase terdeteksi
- **Original** (70%): 70 abstrak original

**Ground Truth:**
- Verifikasi manual oleh 3 reviewer (dosen)
- Agreement minimum 80%
- Dokumentasi sumber plagiarisme

### 5.3 Data Collection

1. **Pengumpulan abstrak** dari perpustakaan digital
2. **Anonymisasi** data (hapus nama mahasiswa)
3. **Preprocessing** (convert ke format standar)
4. **Labeling** manual untuk ground truth
5. **Validation** oleh expert

---

## 6. Evaluasi Sistem

### 6.1 Metrik Evaluasi

#### A. Confusion Matrix

```
                Predicted
              ┌──────────┬──────────┐
              │ Plagiat  │ Original │
    ┌─────────┼──────────┼──────────┤
Ac  │ Plagiat │   TP     │    FN    │
tu  ├─────────┼──────────┼──────────┤
al  │Original │   FP     │    TN    │
    └─────────┴──────────┴──────────┘
```

#### B. Metrik Akurasi

**Accuracy:**
```
         TP + TN
Acc = ─────────────
      TP+TN+FP+FN
```

**Precision:**
```
           TP
Prec = ─────────
       TP + FP
```

**Recall:**
```
           TP
Rec = ─────────
      TP + FN
```

**F1-Score:**
```
           2 × Precision × Recall
F1 = ───────────────────────────────
      Precision + Recall
```

### 6.2 Target Performa

| Metrik | Target | Kategori |
|--------|--------|----------|
| Accuracy | ≥ 85% | Baik |
| Precision | ≥ 80% | Baik |
| Recall | ≥ 85% | Baik |
| F1-Score | ≥ 82% | Baik |

### 6.3 Analisis Error

**False Positive (FP):**
- Teks original terdeteksi sebagai plagiat
- Penyebab: Topik umum dengan banyak literatur similar

**False Negative (FN):**
- Plagiat tidak terdeteksi
- Penyebab: Parafrase sangat ekstensif, referensi tidak di Google

---

## 7. Batasan Penelitian

### 7.1 Batasan Teknis

1. **Bahasa**: Hanya Indonesia & Inggris
2. **Format**: Hanya file PDF
3. **Quota API**: Google CSE limited (100 queries/day gratis)
4. **Scope**: Hanya deteksi, bukan prevention

### 7.2 Batasan Metodologis

1. **Referensi**: Hanya dari sumber yang terindeks Google
2. **Akurasi SBERT**: Tergantung kualitas model pre-trained
3. **Threshold**: Perlu tuning untuk hasil optimal
4. **Context**: Tidak mempertimbangkan kutipan sah

---

## 8. Kontribusi Penelitian

### 8.1 Kontribusi Teoritis

- Menerapkan state-of-the-art NLP untuk deteksi plagiarisme
- Validasi efektivitas Sentence-BERT untuk konteks Indonesia
- Framework untuk semantic similarity detection

### 8.2 Kontribusi Praktis

- Tool gratis untuk institusi akademik
- Mengurangi beban manual checking dosen
- Meningkatkan integritas akademik

### 8.3 Implikasi untuk Fakultas

- Standarisasi proses verifikasi skripsi
- Database hasil deteksi untuk analisis tren
- Deterrent effect untuk plagiarisme

---

## 9. Rencana Pengembangan

### 9.1 Short-term (3-6 bulan)

- [ ] Optimasi model untuk bahasa Indonesia
- [ ] Integrasi database internal skripsi UNISMUH
- [ ] Mobile app version

### 9.2 Long-term (1-2 tahun)

- [ ] Multi-language support (seluruh bahasa Indonesia)
- [ ] Detection untuk full paper (bukan hanya abstrak)
- [ ] Integration dengan sistem akademik

---

## 10. Referensi Metodologi

### Paper Utama:

1. **Sentence-BERT**: Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.

2. **Plagiarism Detection**: Alzahrani, S. M., et al. (2012). Understanding Plagiarism Linguistic Patterns, Textual Features, and Detection Methods.

3. **Semantic Similarity**: Cer, D., et al. (2018). Universal Sentence Encoder.

### Tools & Libraries:

- Sentence-Transformers: https://www.sbert.net/
- Google Custom Search: https://developers.google.com/custom-search
- FastAPI: https://fastapi.tiangolo.com/

---

**Dokumentasi ini merupakan bagian dari skripsi:**
*"Integrasi Google Custom Search Engine (CSE) dan Sentence-BERT untuk Deteksi Plagiarisme Semantik pada Skripsi Mahasiswa Teknik UNISMUH Makassar"*
