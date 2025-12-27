# Panduan Pengambilan Screenshot untuk Dokumentasi Skripsi

## Daftar Screenshot yang Diperlukan

### 1. Architecture Diagram (`architecture_diagram.png`)
**Cara membuat:**
- Gunakan draw.io, Lucidchart, atau tools diagram lainnya
- Gambar:
  - Layer 1: Frontend (React)
  - Layer 2: Backend API (FastAPI)
  - Layer 3: SBERT Model + Google CSE + Corpus
  - Panah menunjukkan data flow
- Export sebagai PNG (1920x1080 recommended)

---

### 2. UI Upload Document (`ui_upload.png`)
**Cara screenshot:**
1. Buka browser ke `http://localhost:3000`
2. Pastikan halaman utama dengan upload form terlihat jelas
3. Screenshot full page dengan:
   - Upload button
   - Options (Google Search, Local Corpus toggles)
   - Health status indicator
4. Save sebagai `docs/images/ui_upload.png`

**Tool:**
- Browser DevTools (F12) → Screenshot full page
- Extension: Nimbus Screenshot, Awesome Screenshot

---

### 3. UI Results (`ui_results.png`)
**Cara screenshot:**
1. Setelah upload dan deteksi selesai
2. Screenshot halaman hasil dengan:
   - Tabel segmen dengan similarity scores
   - Chart pie/bar untuk statistik
   - Source links terlihat
   - Contoh detail segment saat di-klik
3. Save sebagai `docs/images/ui_results.png`

---

### 4. Corpus Info Dashboard (`corpus_info.png`)
**Cara screenshot:**
1. Akses endpoint `/api/corpus/info` di browser atau Postman
2. Screenshot JSON response atau buat UI dashboard
3. Tampilkan:
   - Total segments: 58,300
   - Number of sources: 100
   - Sample sources dengan jumlah segments
4. Save sebagai `docs/images/corpus_info.png`

**Alternatif:** Screenshot dari Postman/Thunder Client dengan formatted JSON

---

### 5. Health Status (`health_status.png`)
**Cara screenshot:**
1. Akses `http://localhost:8000/health` di browser
2. Format JSON dengan:
   ```json
   {
     "status": "healthy",
     "services": {
       "api": "running",
       "sbert_model": "loaded",
       "google_cse": "available"
     }
   }
   ```
3. Screenshot dengan timestamp terlihat
4. Save sebagai `docs/images/health_status.png`

---

### 6. Backend API Docs (`api_docs.png`) - BONUS
**Cara screenshot:**
1. Akses `http://localhost:8000/docs` (FastAPI Swagger UI)
2. Screenshot halaman dengan:
   - List semua endpoints
   - Expand 1-2 endpoint untuk show request/response schema
3. Save sebagai `docs/images/api_docs.png`

---

### 7. Processing Demo (`processing_demo.gif`) - BONUS
**Cara membuat:**
1. Install screen recorder: OBS Studio, ShareX, atau LICEcap
2. Record video:
   - Upload document
   - Show progress indicator
   - Display results
   - Click segment untuk detail
3. Convert to GIF atau keep as MP4
4. Save sebagai `docs/images/processing_demo.gif`

---

## Tools Recommended

**Screenshot:**
- Windows: Snipping Tool, ShareX
- Mac: Command+Shift+4
- Linux: GNOME Screenshot, Flameshot
- Browser: DevTools → Capture screenshot

**Screen Recording:**
- OBS Studio (free, open-source)
- ShareX (Windows)
- LICEcap (lightweight GIF recorder)
- Kazam (Linux)

**Diagram:**
- draw.io / diagrams.net (free, online)
- Lucidchart
- Microsoft Visio
- PlantUML (code-based)

---

## Tips untuk Screenshot Berkualitas

1. **Resolution**: Minimum 1280x720, recommended 1920x1080
2. **Format**: PNG untuk UI, JPG untuk gambar besar
3. **Clarity**: Pastikan text readable, tidak blur
4. **Cropping**: Crop unnecessary parts (browser chrome, taskbar)
5. **Annotations**: Tambahkan arrows/boxes untuk highlight fitur penting
6. **Consistency**: Gunakan theme/color scheme yang sama untuk semua screenshot

---

## Checklist Screenshot

- [ ] `architecture_diagram.png` - Diagram arsitektur sistem
- [ ] `ui_upload.png` - Halaman upload dokumen
- [ ] `ui_results.png` - Halaman hasil deteksi
- [ ] `corpus_info.png` - Info korpus (JSON atau dashboard)
- [ ] `health_status.png` - Health check response
- [ ] `api_docs.png` - FastAPI Swagger UI (bonus)
- [ ] `processing_demo.gif` - Video demo (bonus)

---

## Placeholder Sementara

Jika screenshot belum tersedia, buat placeholder dengan text:

```
[Screenshot akan ditambahkan]
Gambar: Tampilan interface upload dokumen
```

Tambahkan actual screenshot sebelum cetak/submit skripsi.
