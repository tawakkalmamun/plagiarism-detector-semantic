# 📚 Panduan Instalasi dan Setup

## Sistem Deteksi Plagiarisme Semantik
**Integrasi Google CSE dan Sentence-BERT**

---

## 📋 Requirements

### System Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), atau macOS
- **RAM**: Minimum 8GB (Recommended 16GB)
- **Storage**: 5GB free space
- **Internet**: Koneksi stabil untuk Google API

### Software Requirements
- **Python**: 3.8 atau lebih tinggi
- **Node.js**: 16.x atau lebih tinggi
- **Git**: Untuk version control
- **Google Chrome/Firefox**: Browser modern

---

## 🚀 Instalasi Backend (Python)

### 1. Clone Repository
```bash
git clone <repository-url>
cd plagiarism-detector-semantic
```

### 2. Setup Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

**Note**: Instalasi Sentence-BERT dan PyTorch memerlukan waktu (5-10 menit)

### 4. Download Model SBERT (Otomatis)
Model akan otomatis ter-download saat pertama kali dijalankan (~500MB)

### 5. Setup Google Custom Search Engine

#### A. Dapatkan Google API Key
1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Create New Project atau pilih existing project
3. Enable **Custom Search API**:
   - Navigation Menu → APIs & Services → Library
   - Search "Custom Search API" → Enable
4. Create Credentials:
   - APIs & Services → Credentials
   - Create Credentials → API Key
   - Copy API Key

#### B. Setup Custom Search Engine
1. Buka [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click "Add" atau "Create"
3. Setup:
   - **Search the entire web**: ON
   - **Sites to search**: (kosongkan untuk search seluruh web)
   - **Name**: Plagiarism Detector Search
4. Click "Create"
5. Copy **Search Engine ID** dari Control Panel

### 6. Konfigurasi Environment Variables
```bash
# Copy template
cp .env.example .env

# Edit .env file
nano .env  # atau gunakan text editor lain
```

Isi `.env`:
```env
GOOGLE_API_KEY=AIzaSy...
GOOGLE_CSE_ID=0123456789abc...
```

### 7. Test Backend
```bash
# Test instalasi
python test_system.py

# Run server
python main.py
```

Server akan berjalan di: `http://localhost:8000`

Akses API Documentation: `http://localhost:8000/docs`

---

## 🎨 Instalasi Frontend (React)

### 1. Install Node Modules
```bash
cd frontend
npm install
```

**Note**: Proses instalasi memerlukan 2-3 menit

### 2. Konfigurasi API URL
Buat file `.env` di folder `frontend`:
```bash
REACT_APP_API_URL=http://localhost:8000
```

### 3. Run Development Server
```bash
npm start
```

Browser akan otomatis membuka: `http://localhost:3000`

### 4. Build untuk Production
```bash
npm run build
```

Output ada di folder `build/`

---

## 🧪 Testing System

### Backend Testing
```bash
cd backend
python test_system.py
```

Test akan meliputi:
- ✅ Text Segmentation
- ✅ Similarity Calculation
- ✅ Classification Logic
- ✅ Text Preprocessing
- ✅ Full Detection Pipeline

### Frontend Testing
```bash
cd frontend
npm test
```

---

## 📝 Cara Penggunaan

### 1. Via Web Interface

1. **Start Backend**:
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm start
   ```

3. **Akses Aplikasi**: `http://localhost:3000`

4. **Upload PDF**: 
   - Click "Pilih File PDF"
   - Select abstrak.pdf
   - Adjust threshold (default: 0.75)
   - Click "Deteksi Plagiarisme"

5. **Lihat Hasil**:
   - Summary statistics
   - Charts (Pie & Bar)
   - Detail per segment
   - Download CSV report

### 2. Via API (cURL)

```bash
# Detect plagiarism from PDF
curl -X POST "http://localhost:8000/api/detect" \
  -F "file=@abstrak.pdf" \
  -F "threshold=0.75" \
  -F "use_search=true" \
  -F "extract_abstract=false"

# Detect from raw text
curl -X POST "http://localhost:8000/api/detect-text" \
  -F "text=Penelitian ini bertujuan..." \
  -F "threshold=0.75"

# Get result by task_id
curl "http://localhost:8000/api/result/{task_id}"

# Download CSV
curl "http://localhost:8000/api/download/{task_id}" -o report.csv
```

### 3. Via Python Script

```python
from plagiarism_detector import PlagiarismDetector

# Initialize
detector = PlagiarismDetector(
    google_api_key="YOUR_KEY",
    google_cse_id="YOUR_CSE_ID",
    similarity_threshold=0.75
)

# Detect dari file
result = detector.detect_from_file("abstrak.pdf")

# Detect dari text
text = "Penelitian ini bertujuan untuk..."
result = detector.detect_plagiarism(text)

# Print results
print(f"Plagiarism: {result['plagiarism_percentage']}%")
for detail in result['details']:
    print(f"Segment {detail['segment_id']}: {detail['label']}")
```

---

## 🔧 Troubleshooting

### Problem: Module Not Found
```bash
# Solution: Install requirements lagi
pip install -r requirements.txt
```

### Problem: Google API Error
```bash
# Check:
# 1. API Key valid?
# 2. Custom Search API enabled?
# 3. Quota tidak habis? (100 queries/day gratis)
```

### Problem: SBERT Model Error
```bash
# Solution: Download manual
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')"
```

### Problem: Port Already in Use
```bash
# Backend (port 8000)
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Frontend (port 3000)
# Edit package.json: "start": "PORT=3001 react-scripts start"
```

### Problem: PDF Extraction Failed
```bash
# Install alternative PDF library
pip install pdfminer.six
```

---

## 📊 API Quota Management

### Google Custom Search
- **Free Tier**: 100 queries/day
- **Paid Tier**: $5 per 1000 queries

### Tips Menghemat Quota:
1. Gunakan `use_search=false` untuk testing
2. Cache hasil search
3. Batch processing
4. Upgrade ke paid tier jika diperlukan

---

## 🎯 Optimasi Performance

### Backend
```python
# Adjust segment size
detector = PlagiarismDetector(segment_size=30)  # Lebih besar = lebih cepat

# Disable search untuk testing
result = detector.detect_plagiarism(text, use_search=False)
```

### Frontend
```bash
# Build optimized version
npm run build

# Serve dengan web server
npx serve -s build
```

---

## 📦 Deployment

### Backend Deployment (Heroku)
```bash
# Install Heroku CLI
heroku login
heroku create plagiarism-api

# Add Procfile
echo "web: uvicorn main:app --host=0.0.0.0 --port=${PORT}" > Procfile

# Deploy
git push heroku main
```

### Frontend Deployment (Vercel)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

---

## 📚 Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Sentence-BERT](https://www.sbert.net/)
- [Google Custom Search](https://developers.google.com/custom-search)
- [React Documentation](https://react.dev/)

### Dataset Sample
- Abstrak skripsi tersedia di folder `data/`
- PDF samples untuk testing

---

## 🆘 Support

Jika mengalami masalah:
1. Check troubleshooting guide
2. Review logs di `backend/logs/`
3. Open issue di repository
4. Contact: [your-email]

---

## ✅ Checklist Setup

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Google API Key obtained
- [ ] Google CSE ID obtained
- [ ] .env file configured
- [ ] SBERT model downloaded
- [ ] Backend running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] Test detection successful

---

**Selamat! Sistem siap digunakan! 🎉**
