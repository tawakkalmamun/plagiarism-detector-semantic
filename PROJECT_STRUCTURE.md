# 📁 Struktur Project

## Sistem Deteksi Plagiarisme Semantik

```
plagiarism-detector-semantic/
│
├── 📄 README.md                     # Dokumentasi utama project
├── 📄 QUICKSTART.md                 # Panduan quick start
├── 📄 LICENSE                       # MIT License
├── 📄 .gitignore                    # Git ignore rules
│
├── 📂 backend/                      # Backend API (Python/FastAPI)
│   ├── 📄 main.py                   # FastAPI application entry point
│   ├── 📄 requirements.txt          # Python dependencies
│   ├── 📄 test_system.py            # Testing script
│   ├── 📄 .env.example              # Environment variables template
│   │
│   ├── 📂 core/                     # Core detection logic
│   │   ├── 📄 __init__.py
│   │   ├── 📄 plagiarism_detector.py   # Main detector class (SBERT + Google CSE)
│   │   └── 📄 pdf_processor.py         # PDF text extraction
│   │
│   ├── 📂 api/                      # API endpoints (auto-created)
│   ├── 📂 models/                   # Data models (auto-created)
│   ├── 📂 utils/                    # Utility functions (auto-created)
│   ├── 📂 uploads/                  # Temporary file uploads
│   ├── 📂 results/                  # Detection results (CSV)
│   └── 📂 logs/                     # Application logs
│
├── 📂 frontend/                     # Frontend Web App (React)
│   ├── 📄 package.json              # Node.js dependencies
│   │
│   ├── 📂 public/
│   │   └── 📄 index.html            # HTML template
│   │
│   ├── 📂 src/
│   │   ├── 📄 index.js              # React entry point
│   │   ├── 📄 index.css             # Global styles
│   │   ├── 📄 App.js                # Main React component
│   │   └── 📄 App.css               # Component styles
│   │
│   ├── 📂 build/                    # Production build (generated)
│   └── 📂 node_modules/             # Node dependencies (generated)
│
├── 📂 data/                         # Sample data & testing
│   └── 📄 sample_data.py            # Sample abstracts untuk testing
│
├── 📂 docs/                         # Dokumentasi
│   ├── 📄 INSTALLATION.md           # Panduan instalasi lengkap
│   └── 📄 METHODOLOGY.md            # Dokumentasi metodologi penelitian
│
└── 📂 results/                      # Output results (CSV reports)

```

---

## 📊 File Descriptions

### Backend Files

| File | Deskripsi | Lines |
|------|-----------|-------|
| `main.py` | FastAPI server dengan endpoints API | ~500 |
| `plagiarism_detector.py` | Core logic: segmentation, search, SBERT | ~400 |
| `pdf_processor.py` | Extract text dari PDF files | ~200 |
| `test_system.py` | Unit testing untuk semua komponen | ~300 |

### Frontend Files

| File | Deskripsi | Lines |
|------|-----------|-------|
| `App.js` | Main UI dengan upload, detection, visualization | ~600 |
| `App.css` | Styling untuk responsive design | ~300 |

### Documentation Files

| File | Deskripsi | Pages |
|------|-----------|-------|
| `README.md` | Overview & quick info | 5 |
| `QUICKSTART.md` | Setup cepat 5 menit | 3 |
| `INSTALLATION.md` | Panduan instalasi detail | 10 |
| `METHODOLOGY.md` | Metodologi penelitian | 15 |

---

## 🔧 Auto-Generated Folders

Folder berikut akan otomatis dibuat saat runtime:

- `backend/uploads/` - Temporary PDF uploads
- `backend/results/` - CSV detection reports
- `backend/logs/` - Application logs
- `frontend/build/` - Production build
- `frontend/node_modules/` - Node dependencies

---

## 📦 Key Dependencies

### Backend (Python)
```
fastapi==0.104.1           # Web framework
sentence-transformers       # SBERT model
google-api-python-client   # Google CSE
PyPDF2/pdfplumber          # PDF processing
pandas                     # Data handling
```

### Frontend (React)
```
react==18.2.0              # UI framework
@mui/material              # UI components
chart.js                   # Visualization
axios                      # HTTP client
react-pdf                  # PDF viewer
```

---

## 🎯 Main Entry Points

### Development
```bash
# Backend
python backend/main.py
→ http://localhost:8000

# Frontend
cd frontend && npm start
→ http://localhost:3000
```

### Testing
```bash
# Run all tests
python backend/test_system.py

# Test specific function
pytest backend/tests/
```

### Production
```bash
# Build frontend
cd frontend && npm run build

# Run backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## 📈 Code Statistics

| Language | Files | Lines | Comments |
|----------|-------|-------|----------|
| Python   | 5     | 1800  | 300      |
| JavaScript | 4   | 1200  | 150      |
| CSS      | 2     | 400   | 50       |
| Markdown | 5     | 2000  | -        |
| **Total** | **16** | **5400** | **500** |

---

## 🚀 Next Steps After Setup

1. ✅ Install dependencies (backend & frontend)
2. ✅ Setup Google API credentials
3. ✅ Test with sample data
4. ✅ Deploy to production
5. ✅ Collect real data for evaluation
6. ✅ Write thesis documentation

---

## 📚 Additional Resources

- API Documentation: `http://localhost:8000/docs`
- Sample Data: `data/sample_data.py`
- Test Cases: `backend/test_system.py`
- Issue Tracker: GitHub Issues (if applicable)

---

**Last Updated**: 2025-01-16  
**Version**: 1.0.0  
**Author**: Mahasiswa Teknik Informatika UNISMUH Makassar
