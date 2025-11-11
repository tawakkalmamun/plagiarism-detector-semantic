# 🚀 Quick Start Guide

## Deteksi Plagiarisme Semantik - Setup Cepat

---

## ⚡ Instalasi Cepat (5 Menit)

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env: masukkan GOOGLE_API_KEY dan GOOGLE_CSE_ID
python main.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 3. Buka Browser
```
http://localhost:3000
```

---

## 📝 Cara Pakai (3 Langkah)

### 1. Upload PDF
- Click **"Pilih File PDF"**
- Select file abstrak skripsi (.pdf)

### 2. Atur Pengaturan (Opsional)
- **Threshold**: 0.75 (default)
- **Google Search**: ON (recommended)
- **Hanya Abstrak**: ON/OFF

### 3. Deteksi
- Click **"Deteksi Plagiarisme"**
- Tunggu 30-60 detik
- Lihat hasil analisis

---

## 📊 Interpretasi Hasil

### Persentase Plagiarisme
- **< 20%**: AMAN ✅ (Acceptable)
- **20-40%**: HATI-HATI ⚠️ (Need Review)
- **> 40%**: BAHAYA ❌ (High Plagiarism)

### Skor Kemiripan per Segmen
- **≥ 0.75**: Terindikasi Plagiat
- **< 0.75**: Original

### Status
- 🔴 **Plagiat**: Similarity ≥ threshold
- 🟢 **Original**: Similarity < threshold

---

## 🎯 Tips Penggunaan

### 1. Untuk Mahasiswa
- ✅ Cek draft sebelum submit
- ✅ Review segmen yang terdeteksi
- ✅ Perbaiki parafrase yang terlalu mirip
- ❌ Jangan hanya mengganti kata sinonim
- ❌ Jangan copy-paste dari internet

### 2. Untuk Dosen
- ✅ Verifikasi hasil sistem secara manual
- ✅ Check sumber yang terdeteksi
- ✅ Export CSV untuk dokumentasi
- ✅ Diskusikan dengan mahasiswa jika ada temuan

### 3. Optimasi Deteksi
- **Threshold 0.75**: Standard (recommended)
- **Threshold 0.80**: Lebih ketat
- **Threshold 0.70**: Lebih longgar

---

## 🔑 Dapatkan Google API Key (10 Menit)

### Step 1: Google Cloud Console
1. Buka: https://console.cloud.google.com/
2. Create Project baru
3. Enable "Custom Search API"
4. Create API Key
5. **Copy API Key**

### Step 2: Custom Search Engine
1. Buka: https://programmablesearchengine.google.com/
2. Create Search Engine
3. Set: "Search the entire web"
4. **Copy Search Engine ID**

### Step 3: Setup .env
```env
GOOGLE_API_KEY=AIzaSy...
GOOGLE_CSE_ID=0123456789abc...
```

---

## ❓ FAQ

**Q: Sistem tidak bisa akses internet?**
A: Check firewall/proxy. Sistem perlu akses ke Google API.

**Q: API Key error?**
A: Pastikan Custom Search API sudah enabled di Google Cloud Console.

**Q: Quota habis?**
A: Free tier = 100 queries/day. Upgrade atau tunggu reset besok.

**Q: Hasil tidak akurat?**
A: Adjust threshold atau review manual hasil deteksi.

**Q: Support file Word?**
A: Saat ini hanya PDF. Convert Word → PDF dulu.

---

## 🐛 Troubleshooting Cepat

### Backend tidak running?
```bash
# Check Python version
python --version  # Harus 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port
netstat -ano | findstr :8000
```

### Frontend error?
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Harus 16+
```

### Model SBERT error?
```bash
# Download manual
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')"
```

---

## 📞 Butuh Bantuan?

1. **Baca dokumentasi lengkap**: `docs/INSTALLATION.md`
2. **Check metodologi**: `docs/METHODOLOGY.md`
3. **Lihat contoh**: `data/sample_data.py`
4. **Test sistem**: `python test_system.py`

---

## 🎓 Untuk Skripsi

### Yang Perlu Dijelaskan:
1. ✅ Alur sistem (flowchart)
2. ✅ Algoritma SBERT & Cosine Similarity
3. ✅ Sliding window technique
4. ✅ Evaluasi akurasi (confusion matrix)
5. ✅ Hasil pengujian dengan sample data

### Bab-bab Penting:
- **BAB 2**: Landasan Teori (NLP, SBERT, Plagiarism)
- **BAB 3**: Metodologi (dijelaskan di METHODOLOGY.md)
- **BAB 4**: Implementasi (screenshot sistem)
- **BAB 5**: Hasil & Pembahasan (akurasi, evaluasi)

---

## ✨ Fitur Utama

- 🔍 Deteksi semantik (parafrase)
- 📊 Visualisasi hasil (charts)
- 📥 Export laporan (CSV)
- 🌐 Multi-bahasa (ID & EN)
- ⚡ Real-time detection
- 🎯 Adjustable threshold

---

**Happy Detecting! 🎉**

Sistem ini dikembangkan untuk membantu meningkatkan integritas akademik di Fakultas Teknik UNISMUH Makassar.
