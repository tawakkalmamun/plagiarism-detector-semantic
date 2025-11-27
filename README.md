# Sistem Deteksi Plagiarisme Semantik untuk Skripsi Mahasiswa

**Integrasi Google Custom Search Engine (CSE) dan Sentence-BERT**  
Fakultas Teknik UNISMUH Makassar

> Tagline: Sistem Deteksi Plagiarisme Semantik menggunakan Google CSE dan Sentence-BERT

## 📋 Deskripsi Project

Sistem deteksi plagiarisme berbasis semantik yang mampu mendeteksi kemiripan makna (bukan hanya literal) pada abstrak skripsi mahasiswa. Sistem ini menggunakan:
- **Google Custom Search Engine (CSE)** untuk pencarian referensi dari web (opsional)
- **Local Corpus** untuk pembanding dengan skripsi lama yang sudah ada ⭐ **BARU**
- **Sentence-BERT (SBERT)** untuk analisis kemiripan semantik
- **Sliding Window Technique** untuk segmentasi teks
- **Cosine Similarity** untuk pengukuran kemiripan

### 🆕 Mode Deteksi yang Tersedia:
1. **Web Search Mode**: Bandingkan dengan konten internet via Google CSE
2. **Local Corpus Mode**: Bandingkan dengan koleksi skripsi lama (100+ PDF/TXT)
3. **Hybrid Mode**: Kombinasi keduanya untuk deteksi komprehensif

## 🎯 Fitur Utama

✅ Deteksi plagiarisme semantik (mendeteksi parafrase)  
✅ **Local corpus dari skripsi lama (PDF/TXT)** ⭐ BARU  
✅ Upload file PDF abstrak  
✅ Segmentasi otomatis per 25 kata  
✅ Pencarian snippet referensi dari Google (opsional)  
✅ Analisis kemiripan menggunakan AI (SBERT)  
✅ **Batch build corpus dari folder** ⭐ BARU  
✅ Export hasil ke CSV  
✅ Dashboard visualisasi hasil deteksi  
✅ Laporan detail per segmen  
✅ **API endpoints untuk corpus management** ⭐ BARU  

## 🏗️ Arsitektur Sistem

```
plagiarism-detector-semantic/
├── backend/                 # Backend API (Python/FastAPI)
│   ├── api/                # API endpoints
│   ├── core/               # Core detection logic
│   ├── models/             # Data models
│   ├── utils/              # Utility functions
│   └── requirements.txt
├── frontend/               # Frontend (React)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
├── data/                   # Sample data untuk testing
├── results/                # Output hasil deteksi
└── docs/                   # Dokumentasi tambahan
```

## 🚀 Cara Instalasi

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Custom Search API Key
- Google Search Engine ID

### Backend Setup

 
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## 📖 Cara Penggunaan

### Mode 1: Deteksi dengan Google CSE (Web Search)

**Via Web Interface:**
1. Buka browser: `http://localhost:3000`
2. Upload file PDF abstrak
3. Aktifkan "Gunakan Google Search"
4. Klik "Deteksi Plagiarisme"
5. Lihat hasil analisis
6. Download laporan CSV

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/detect" \
  -F "file=@abstrak.pdf" \
  -F "threshold=0.75" \
  -F "use_search=true"
```

### Mode 2: Deteksi dengan Local Corpus (Skripsi Lama) ⭐ BARU

**1. Persiapan Corpus:**
```bash
# Siapkan folder corpus
mkdir -p backend/uploads/corpus_skripsi

# Copy skripsi lama (PDF/TXT) ke folder tersebut
cp /path/to/old/skripsi/*.pdf backend/uploads/corpus_skripsi/
```

**2. Build Corpus:**
```bash
cd backend
python build_corpus.py --folder uploads/corpus_skripsi --extension .pdf
```

Output:
```
📊 HASIL BUILD CORPUS
=====================
✅ Success: True
📁 Files processed: 100/100
📝 Total segments: 4250
💾 Corpus size: 4250
```

**3. Deteksi dengan Corpus:**
```bash
curl -X POST "http://localhost:8000/api/detect" \
  -F "file=@skripsi_baru.pdf" \
  -F "threshold=0.75" \
  -F "use_local_corpus=true" \
  -F "use_search=false"
```

**4. Cek Info Corpus:**
```bash
curl http://localhost:8000/api/corpus/info
```

### Mode 3: Hybrid (Google CSE + Local Corpus)
Gunakan keduanya untuk deteksi paling komprehensif:
```bash
curl -X POST "http://localhost:8000/api/detect" \
  -F "file=@abstrak.pdf" \
  -F "use_search=true" \
  -F "use_local_corpus=true"
```

### Via Python Script
```bash
curl -X POST "http://localhost:8000/api/detect" \
  -F "file=@abstrak.pdf" \
  -F "threshold=0.75"
```

### Via Python Script
```python
from plagiarism_detector import PlagiarismDetector

# Initialize dengan atau tanpa Google CSE
detector = PlagiarismDetector() 

# Build corpus dari folder (opsional)
result = detector.build_corpus_from_folder("uploads/corpus_skripsi", ".pdf")
print(f"Corpus built: {result['total_segments']} segments")

# Deteksi plagiarisme
result = detector.detect_from_file("skripsi_baru.pdf", use_local_corpus=True)
print(result)
```

## 📊 Endpoint API Corpus Management

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/api/corpus/build` | POST | Build corpus dari folder PDF/TXT |
| `/api/corpus/info` | GET | Informasi corpus (size, sources) |
| `/api/corpus/clear` | DELETE | Hapus semua corpus |

**Contoh Build Corpus via API:**
```bash
curl -X POST "http://localhost:8000/api/corpus/build" \
  -F "folder_path=uploads/corpus_skripsi" \
  -F "file_extension=.pdf" \
  -F "clear_existing=false"
```

## 🔬 Metodologi

### 1. Text Extraction
- PDF → Plain Text menggunakan PyPDF2/pdfplumber

### 2. Segmentation (Sliding Window)
- Teks dibagi per 25 kata
- Overlap 5 kata untuk kontinuitas

### 3. Reference Search (Google CSE)
- Setiap segment dicari di Google
- Ambil top 5 snippets
- Filter hasil yang relevan

### 4. Semantic Comparison (SBERT)
- Model: `paraphrase-multilingual-mpnet-base-v2`
- Encoding: Segment + Snippets → Vectors
- Similarity: Cosine Similarity
- Threshold: 0.75 (default, bisa disesuaikan)

### 5. Classification
```python
if similarity >= 0.75:
    label = "Plagiat"
else:
    label = "Original"
```

## 📊 Format Output

### CSV Report
```csv
segment_id,segment_text,best_match,similarity_score,label,source_url
1,"Penelitian ini bertujuan untuk...","This research aims to...",0.89,Plagiat,https://example.com
2,"Metode yang digunakan adalah...","The method used is...",0.92,Plagiat,https://example2.com
3,"Hasil penelitian menunjukkan...","Results show that...",0.65,Original,-
```

### JSON Response
```json
{
  "filename": "abstrak_001.pdf",
  "total_segments": 15,
  "plagiarized_segments": 8,
  "original_segments": 7,
  "plagiarism_percentage": 53.33,
  "avg_similarity": 0.74,
  "details": [...]
}
```

## 🧪 Testing

```bash
# Unit tests
cd backend
pytest tests/

# Integration tests
pytest tests/integration/

# Load test
locust -f tests/load_test.py
```

## 📈 Hasil Penelitian yang Diharapkan

1. **Akurasi Deteksi**: Target ≥ 85%
2. **Precision**: Kemampuan identifikasi positif benar
3. **Recall**: Kemampuan menemukan semua kasus plagiarisme
4. **F1-Score**: Keseimbangan precision dan recall

## 🔒 Batasan Sistem

- Hanya untuk teks berbahasa Indonesia dan Inggris
- Bergantung pada ketersediaan hasil di Google
- API quota Google CSE terbatas (100 query/day gratis)
- Memerlukan koneksi internet

## 🛠️ Teknologi yang Digunakan

### Backend
- Python 3.9
- FastAPI (Web Framework)
- Sentence-Transformers (SBERT)
- PyPDF2/pdfplumber (PDF Processing)
- Google API Client
- Pandas (Data Processing)

### Frontend
- React 18
- Material-UI (MUI)
- Axios (HTTP Client)
- Chart.js (Visualization)
- React-PDF (PDF Viewer)

## 📝 Lisensi

MIT License - Untuk keperluan akademik UNISMUH Makassar

## 👥 Author

Mahasiswa Teknik Informatika  
Universitas Muhammadiyah Makassar  
Tahun 2025

## 📞 Kontak & Support

Untuk pertanyaan atau bantuan:
- Email: [your-email]
- GitHub Issues: [repository-url]

## 🙏 Acknowledgments

- Fakultas Teknik UNISMUH Makassar
- Dosen Pembimbing
- Google Custom Search Engine
- Sentence-Transformers Library

---

**⚠️ Disclaimer**: Sistem ini dikembangkan untuk tujuan penelitian dan pendidikan. Hasil deteksi sebaiknya diverifikasi manual oleh dosen pembimbing.
