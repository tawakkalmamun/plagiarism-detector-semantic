# Template Tabel Hasil Pengujian

## Tabel 4.1 - Hasil Pengujian Fungsional Upload Dokumen

| No | Test Case | Input | Expected Result | Actual Result | Status |
|----|-----------|-------|-----------------|---------------|--------|
| 1 | Upload PDF Valid | File PDF 2.5 MB, 10 hal | Upload success, 42 segmen | Upload success, 42 segmen | ✓ PASS |
| 2 | Upload TXT Valid | File TXT 50 KB | Upload success, 18 segmen | Upload success, 18 segmen | ✓ PASS |
| 3 | Upload DOCX Invalid | File DOCX | Error "Format tidak didukung" | Error ditampilkan | ✓ PASS |
| 4 | Upload File Besar | File PDF 25 MB | Error "File terlalu besar" | Error ditampilkan | ✓ PASS |

---

## Tabel 4.2 - Hasil Pengujian Deteksi Plagiarisme

| No | Mode Deteksi | Input Dokumen | Segmen Plagiat | Segmen Original | Akurasi | Waktu Proses |
|----|-------------|---------------|----------------|-----------------|---------|--------------|
| 1 | Google CSE Only | Abstrak paper (15 seg) | 12 (80%) | 3 (20%) | 87.3% | 45 detik |
| 2 | Local Corpus Only | Cuplikan skripsi (20 seg) | 20 (100%) | 0 (0%) | 92.1% | 8 detik |
| 3 | Hybrid Mode | Dok campuran (21 seg) | 13 (62%) | 8 (38%) | 95.0% | 52 detik |
| 4 | Original Text | Teks ditulis sendiri (30 seg) | 2 (7%)* | 28 (93%) | 93.3% | 38 detik |

*False positive minimal (similarity < 45%)

---

## Tabel 4.3 - Performa Endpoint API

| Endpoint | Method | Avg Response Time | Max Response Time | Min Response Time | Status |
|----------|--------|-------------------|-------------------|-------------------|---------|
| `/health` | GET | 45 ms | 120 ms | 25 ms | ✓ PASS |
| `/api/corpus/info` | GET | 180 ms | 350 ms | 100 ms | ✓ PASS |
| `/api/detect` (short) | POST | 8.2 s | 12 s | 5 s | ✓ PASS |
| `/api/detect` (long) | POST | 45 s | 68 s | 35 s | ✓ PASS |

---

## Tabel 4.4 - Penggunaan Resource Sistem

| Kondisi | CPU Usage | RAM Usage | Disk I/O | Network |
|---------|-----------|-----------|----------|---------|
| Idle | 5% | 2.1 GB | Minimal | < 1 KB/s |
| Model Loading | 80% | 3.8 GB | 400 MB/s | < 1 KB/s |
| Detection (CPU) | 95-100% | 4.5 GB | Minimal | 10-50 KB/s |
| Peak Load | 100% | 4.8 GB | Minimal | 100 KB/s |

---

## Tabel 4.5 - Perbandingan dengan Sistem Lain

| Aspek | String Matching | Sistem Ini (Semantic) | Keterangan |
|-------|----------------|----------------------|------------|
| Deteksi Exact Match | ✓✓✓ Sangat Baik | ✓✓ Baik | String matching lebih cepat |
| Deteksi Parafrase | ✗ Tidak Bisa | ✓✓✓ Sangat Baik | SBERT mendeteksi semantic similarity |
| Deteksi Synonym | ✗ Tidak Bisa | ✓✓✓ Sangat Baik | Model understand context |
| Kecepatan | ✓✓✓ Sangat Cepat | ✓ Lambat | Trade-off: accuracy vs speed |
| Resource Usage | ✓✓✓ Ringan | ✓ Berat | Membutuhkan model embedding |
| False Positive Rate | ~15-20% | ~8% | Sistem ini lebih akurat |
| Coverage | Internet only | Internet + Local | Dual source advantage |

Legend: ✓✓✓ Excellent, ✓✓ Good, ✓ Fair, ✗ Poor/Not Available

---

## Tabel 4.6 - Distribusi Sumber Deteksi Plagiarisme

| Sumber | Jumlah Segmen | Persentase | Avg Similarity |
|--------|---------------|------------|----------------|
| Google CSE (Journal) | 245 | 35% | 84.2% |
| Google CSE (Website) | 178 | 25% | 78.5% |
| Local Corpus (Skripsi 2019) | 156 | 22% | 91.3% |
| Local Corpus (Skripsi 2021) | 128 | 18% | 89.7% |
| **Total Plagiat** | **707** | **100%** | **85.9%** |

---

## Tabel 4.7 - Analisis False Positive dan False Negative

| Metrik | Nilai | Keterangan |
|--------|-------|------------|
| True Positive (TP) | 652 | Correctly detected plagiarism |
| True Negative (TN) | 1,240 | Correctly identified original |
| False Positive (FP) | 55 | Original misclassified as plagiat |
| False Negative (FN) | 38 | Plagiat missed by detector |
| **Accuracy** | **95.3%** | (TP+TN)/(TP+TN+FP+FN) |
| **Precision** | **92.2%** | TP/(TP+FP) |
| **Recall** | **94.5%** | TP/(TP+FN) |
| **F1-Score** | **93.3%** | 2×(Precision×Recall)/(Precision+Recall) |

---

## Tabel 4.8 - Karakteristik Korpus Lokal

| Metrik | Nilai |
|--------|-------|
| Jumlah Dokumen | 100 PDF |
| Total Ukuran File | 383 MB |
| Jumlah Segmen | 58,300 |
| Rata-rata Segmen per Dokumen | 583 |
| Ukuran Korpus (dengan embeddings) | 397 MB |
| Dimensi Embedding | 768 |
| Waktu Build Corpus | ~10 menit |
| Success Rate Processing | 98% (98/100) |

---

## Tabel 4.9 - Skalabilitas Sistem

| Skala | Concurrent Users | Documents/Hour | Response Time | Resource | Feasibility |
|-------|-----------------|----------------|---------------|----------|-------------|
| Small (Current) | 3-5 | 10-15 | Acceptable | CPU only | ✓ Deployed |
| Medium | 10-20 | 50-80 | Good | GPU + 8GB RAM | ✓ Feasible |
| Large | 50-100 | 200-300 | Good | Multi-GPU + LB | ⚠ Needs infra |
| Enterprise | 500+ | 1000+ | Excellent | Cluster + Cache | ⚠ Major upgrade |

---

## Cara Menggunakan Tabel Ini

1. **Copy tabel yang dibutuhkan** ke dokumen skripsi Anda
2. **Sesuaikan nilai** dengan hasil pengujian aktual Anda
3. **Format** menggunakan Markdown, LaTeX, atau Word Table
4. **Tambahkan caption** dan penjelasan di bawah tabel
5. **Reference** tabel di body text: "Seperti ditunjukkan pada Tabel 4.1, ..."

## Konversi Format

**Markdown → Word:**
- Paste ke Word → Convert Text to Table

**Markdown → LaTeX:**
```latex
\begin{table}[h]
\centering
\caption{Hasil Pengujian Fungsional}
\begin{tabular}{|l|l|l|l|}
\hline
Test Case & Input & Expected & Status \\
\hline
Upload PDF & 2.5 MB & Success & PASS \\
\hline
\end{tabular}
\end{table}
```

**Markdown → HTML:**
Use Pandoc: `pandoc tables.md -o tables.html`
