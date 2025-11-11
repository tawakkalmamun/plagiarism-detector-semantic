# Sistem Deteksi Plagiarisme Semantik untuk Skripsi Mahasiswa

**Integrasi Google Custom Search Engine (CSE) dan Sentence-BERT**  
Fakultas Teknik UNISMUH Makassar

## 📋 Deskripsi Project

Sistem deteksi plagiarisme berbasis semantik yang mampu mendeteksi kemiripan makna (bukan hanya literal) pada abstrak skripsi mahasiswa. Sistem ini menggunakan:
- **Google Custom Search Engine (CSE)** untuk pencarian referensi dari web
- **Sentence-BERT (SBERT)** untuk analisis kemiripan semantik
- **Sliding Window Technique** untuk segmentasi teks
- **Cosine Similarity** untuk pengukuran kemiripan

## 🎯 Fitur Utama

✅ Deteksi plagiarisme semantik (mendeteksi parafrase)  
✅ Upload file PDF abstrak  
✅ Segmentasi otomatis per 25 kata  
✅ Pencarian snippet referensi dari Google  
✅ Analisis kemiripan menggunakan AI (SBERT)  
✅ Export hasil ke CSV  
✅ Dashboard visualisasi hasil deteksi  
✅ Laporan detail per segmen  

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

```bash
cd backend
pip install -r requirements.txt
```

Buat file `.env`:
```
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_search_engine_id_here
```

Jalankan server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## 📖 Cara Penggunaan

### 1. Via Web Interface
1. Buka browser: `http://localhost:3000`
2. Upload file PDF abstrak
3. Klik "Deteksi Plagiarisme"
4. Lihat hasil analisis
5. Download laporan CSV

### 2. Via API
```bash
curl -X POST "http://localhost:8000/api/detect" \
  -F "file=@abstrak.pdf" \
  -F "threshold=0.75"
```

### 3. Via Python Script
```python
from plagiarism_detector import PlagiarismDetector

detector = PlagiarismDetector()
result = detector.detect_from_file("abstrak.pdf")
print(result)
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
