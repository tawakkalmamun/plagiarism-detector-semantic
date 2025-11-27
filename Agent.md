# 🚀 Panduan Eksekusi Lengkap - Plagiarism Detector

## ✅ CHECKLIST EKSEKUSI

### 🪟 Windows (PowerShell) | 🐧 Linux/Mac (Bash)

---

## 📋 STEP 1: Install Backend Dependencies

### Windows (PowerShell):
```powershell
# Masuk ke folder backend
cd backend

# Install semua Python packages
pip install -r requirements.txt

# Kembali ke root
cd ..
```

### Linux/Mac (Bash):
```bash
# Masuk ke folder backend
cd backend

# Install semua Python packages (gunakan pip3 jika pip tidak tersedia)
pip3 install -r requirements.txt

# Kembali ke root
cd ..
```

**Yang akan diinstall:**
- ✅ FastAPI & Uvicorn (Web framework & server)
- ✅ Sentence-Transformers (SBERT AI model)
- ✅ PyTorch (ML framework) - ~500MB
- ✅ SlowAPI (Rate limiting)
- ✅ Google API Client (CSE integration)
- ✅ PDFPlumber & PyPDF2 (PDF processing)
- ✅ Pandas, Loguru, dan lainnya

**⏱️ Estimasi Waktu:** 5-10 menit (tergantung internet)

**⚠️ Catatan:** First run akan download SBERT model ~500MB

---

## 📋 STEP 2: Setup Environment File

### Windows (PowerShell):
```powershell
# Copy template .env
cd backend
Copy-Item .env.example .env

# Kembali ke root
cd ..
```

### Linux/Mac (Bash):
```bash
# Copy template .env
cd backend
cp .env.example .env

# Kembali ke root
cd ..
```

**Opsional - Edit backend/.env jika ingin Google CSE:**

### Windows:
```powershell
# Buka dengan notepad
notepad backend\.env
```

### Linux/Mac:
```bash
# Buka dengan nano (atau vi/vim)
nano backend/.env

# Atau dengan default editor
gedit backend/.env  # Ubuntu/GNOME
kate backend/.env   # KDE
code backend/.env   # VS Code
```

**Tambahkan (jika punya):**
```bash
GOOGLE_API_KEY=your_key_here
GOOGLE_CSE_ID=your_cse_id_here
```

**Untuk Testing:** Bisa skip edit, sistem akan gunakan mock data

---

## 📋 STEP 3: Install Frontend Dependencies

### Windows (PowerShell):
```powershell
# Masuk ke folder frontend
cd frontend

# Install Node packages
npm install

# Kembali ke root
cd ..
```

### Linux/Mac (Bash):
```bash
# Masuk ke folder frontend
cd frontend

# Install Node packages
npm install

# Kembali ke root
cd ..
```

**Yang akan diinstall:**
- ✅ React & React DOM
- ✅ Material-UI (MUI)
- ✅ Axios (HTTP client)
- ✅ Chart.js (Visualisasi)
- ✅ React Router, dan lainnya

**⏱️ Estimasi Waktu:** 2-3 menit

---

## 📋 STEP 4: Create Required Directories

### Windows (PowerShell):
```powershell
# Buat folder-folder yang diperlukan
New-Item -ItemType Directory -Path backend/uploads -Force
New-Item -ItemType Directory -Path backend/results -Force
New-Item -ItemType Directory -Path backend/logs -Force
```

### Linux/Mac (Bash):
```bash
# Buat folder-folder yang diperlukan
mkdir -p backend/uploads
mkdir -p backend/results
mkdir -p backend/logs
```

**Hasil:** 3 folder baru untuk uploads, results, dan logs

---

## 📋 STEP 5: Start Backend Server

### Windows (PowerShell - Terminal 1):
```powershell
# Masuk ke backend
cd backend

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Linux/Mac (Bash - Terminal 1):
```bash
# Masuk ke backend
cd backend

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Atau jika uvicorn tidak tersedia:
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**⏱️ First Run:** 2-5 menit (download SBERT model)  
**⏱️ Next Runs:** 5-10 detik (load model)

**✅ Server Ready ketika muncul:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**🧪 Test Backend:**
```powershell
# Di browser buka:
# http://localhost:8000/health
# http://localhost:8000/docs
```

**Expected Response (/health):**
```json
{
  "status": "healthy",
  "services": {
    "api": "running",
    "sbert_model": "loaded",
    "google_cse": "not configured"
  }
}
```

---

## 📋 STEP 6: Start Frontend Server

### Windows (PowerShell BARU - Terminal 2):
```powershell
# Masuk ke frontend
cd frontend

# Start React app
npm start
```

### Linux/Mac (Bash BARU - Terminal 2):
```bash
# Masuk ke frontend
cd frontend

# Start React app
npm start
```

**⏱️ Estimasi:** 30 detik - 1 menit

**✅ Ready ketika browser otomatis buka:** `http://localhost:3000`

---

## 📋 STEP 7: Test Upload & Detection

**Di Browser (http://localhost:3000):**

1. ✅ Klik tombol **"Pilih File PDF"**
2. ✅ Upload file (gunakan `test_sample.txt` dari root folder atau PDF apapun)
3. ✅ Atur threshold (default 0.75 = OK)
4. ✅ Klik **"Deteksi Plagiarisme"**
5. ✅ Tunggu proses (5-10 detik)
6. ✅ Lihat hasil deteksi muncul
7. ✅ Download CSV report

**Expected Result:**
- Progress bar muncul
- Hasil deteksi dengan percentage
- Pie chart & bar chart
- Tabel segment details
- Tombol download CSV

---

## 📋 STEP 8: Test API via Swagger

**Di Browser:**

```
http://localhost:8000/docs
```

**Test Steps:**
1. ✅ Expand **POST /api/detect**
2. ✅ Klik **"Try it out"**
3. ✅ Upload file di **"file"** field
4. ✅ Set **threshold** = 0.75
5. ✅ Klik **"Execute"**
6. ✅ Lihat Response body JSON

---

## 📋 STEP 9: Test Rate Limiting

**Test dengan curl atau Postman:**

```powershell
# Test 11 kali cepat (akan di-limit di request ke-11)
for ($i=1; $i -le 11; $i++) {
    Write-Host "Request $i"
    Invoke-RestMethod -Uri "http://localhost:8000/health" -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 100
}
```

**Expected:** Request 11+ akan return **429 Too Many Requests**

**Tunggu 1 menit, coba lagi → should work**

---

## 📋 STEP 10: Check Logs & Monitoring

**Check Logs:**

```powershell
# Lihat log terbaru
Get-Content backend\logs\app_*.log -Tail 50
```

**Check Health:**

```powershell
# PowerShell
Invoke-RestMethod http://localhost:8000/health | ConvertTo-Json -Depth 10
```

**Verify:**
- ✅ `sbert_model`: "loaded"
- ✅ `api`: "running"
- ✅ `rate_limiting`: "enabled"
- ✅ No errors in logs

---

## 🎯 QUICK START - Copy All Commands

### Windows (PowerShell):
```powershell
# Install backend
cd backend
pip install -r requirements.txt
Copy-Item .env.example .env
cd ..

# Install frontend
cd frontend
npm install
cd ..

# Create directories
New-Item -ItemType Directory -Path backend/uploads -Force
New-Item -ItemType Directory -Path backend/results -Force
New-Item -ItemType Directory -Path backend/logs -Force

Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Terminal 1: cd backend && uvicorn main:app --reload" -ForegroundColor White
Write-Host "2. Terminal 2: cd frontend && npm start" -ForegroundColor White
Write-Host "3. Browser: http://localhost:3000" -ForegroundColor White
```

### Linux/Mac (Bash):
```bash
# Install backend
cd backend
pip3 install -r requirements.txt
cp .env.example .env
cd ..

# Install frontend
cd frontend
npm install
cd ..

# Create directories
mkdir -p backend/uploads backend/results backend/logs

echo "✅ Installation Complete!"
echo ""
echo "Next steps:"
echo "1. Terminal 1: cd backend && uvicorn main:app --reload"
echo "2. Terminal 2: cd frontend && npm start"
echo "3. Browser: http://localhost:3000"
```

---

## 🚀 ATAU Gunakan Script Otomatis

### Windows:

**Opsi 1: Setup Script**
```powershell
.\setup.ps1
```

**Opsi 2: Start Script (setelah install)**
```powershell
.\start.ps1
```

### Linux/Mac:

**Opsi 1: Setup Script (buat dulu)**
```bash
chmod +x setup.sh
./setup.sh
```

**Opsi 2: Start Script (buat dulu)**
```bash
chmod +x start.sh
./start.sh
```

---

## ⚡ Troubleshooting Commands

### Check Python:

**Windows:**
```powershell
python --version
```

**Linux/Mac:**
```bash
python3 --version
```

### Check Node:

**Windows & Linux/Mac:**
```bash
node --version
npm --version
```

### Check if port 8000 is used:

**Windows:**
```powershell
netstat -ano | findstr :8000
```

**Linux/Mac:**
```bash
lsof -i :8000
# atau
netstat -tlnp | grep :8000
```

### Kill process on port:

**Windows:**
```powershell
# Get PID from netstat, then:
Stop-Process -Id <PID> -Force
```

**Linux/Mac:**
```bash
# Get PID from lsof, then:
kill -9 <PID>

# Atau langsung:
fuser -k 8000/tcp
```

### Reinstall backend if error:

**Windows:**
```powershell
cd backend
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
cd backend
pip3 uninstall -r requirements.txt -y
pip3 install -r requirements.txt
```

### Clear npm cache if error:

**Windows:**
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules
npm cache clean --force
npm install
```

**Linux/Mac:**
```bash
cd frontend
rm -rf node_modules
npm cache clean --force
npm install
```

---

## 📊 Expected File Structure After Install

```
plagiarism-detector-semantic/
├── backend/
│   ├── .env                    ✅ Created
│   ├── uploads/                ✅ Created
│   ├── results/                ✅ Created
│   ├── logs/                   ✅ Created
│   └── (Python packages installed)
│
├── frontend/
│   └── node_modules/           ✅ Created
│
└── (Root files)
```

---

## ✅ Success Indicators

### Backend Running:
```
✅ INFO: Sentence-BERT model loaded successfully
✅ INFO: Plagiarism Detector initialized successfully
✅ INFO: Application startup complete
✅ INFO: Uvicorn running on http://0.0.0.0:8000
```

### Frontend Running:
```
✅ Compiled successfully!
✅ webpack compiled with 0 errors
✅ On Your Network: http://localhost:3000
```

### Health Check:
```json
✅ "status": "healthy"
✅ "sbert_model": "loaded"
✅ "api": "running"
```

---

## 🎉 SYSTEM READY!

Setelah semua step selesai:
- ✅ Backend API running di port 8000
- ✅ Frontend running di port 3000
- ✅ SBERT model loaded
- ✅ Ready untuk detect plagiarism

**Happy Testing! 🚀**
