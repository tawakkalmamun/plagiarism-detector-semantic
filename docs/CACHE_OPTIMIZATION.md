# SOLUSI: Simpan Model & Dependencies Permanent

## Masalah yang Ingin Dipecahkan

**Sebelum:**
- ❌ Model SBERT download ulang setiap restart (~3 menit)
- ❌ `npm install` ulang setiap kali (~2 menit)
- ❌ Total waktu setup: ~5 menit

**Setelah:**
- ✅ Model cached permanent (~30 detik setup)
- ✅ node_modules cached permanent
- ✅ Total waktu setup: ~30 detik

---

## SOLUSI 1: SBERT Model Cache (IMPLEMENTED)

### Cara Kerja

Huggingface model auto-cache di:
```
~/.cache/huggingface/hub/models--sentence-transformers--paraphrase-multilingual-mpnet-base-v2/
```

**Setup:**
```bash
# First run (auto-download & cache)
python backend/main.py
# Model download: ~3 menit (happens ONCE)

# Restart VS Code
python backend/main.py
# Instant start (model cached!) < 30 detik
```

**Why this works:**
- Cache folder persisten di Codespace
- Tidak perlu di-commit ke Git
- Huggingface handle caching otomatis
- Next restart: cache hit, instant load

**Verifikasi:**
```bash
ls -lh ~/.cache/huggingface/hub/models--sentence-transformers--paraphrase-multilingual-mpnet-base-v2/
# Harus ada ~440 MB setelah first run
```

---

## SOLUSI 2: Node Modules Caching (RECOMMENDED)

### Option A: Commit node_modules Selective (BEST)

**Alasan:**
- npm install hanya ~5 detik jika dependencies sudah ada
- package-lock.json sudah di-commit
- Subsequent restart: npm uses cache

**Cara:**
```bash
# node_modules otomatis di-cache oleh npm dari package-lock.json
npm ci  # clean install (lebih cepat dari npm install)
# First run: 2-3 menit
# Restart: <30 detik (dari npm cache)
```

**Verify npm cache:**
```bash
npm cache ls | head -10
# Harus ada banyak entries
```

### Option B: Include node_modules di Git (Alternative)

Jika ingin 100% instant (tanpa npm install sama sekali):

**Pro:**
- Zero setup time
- Instant node_modules

**Con:**
- Add ~500 MB ke Git
- Slow clone time
- Platform-specific (binary modules)

**Recommend:** Jangan pakai cara ini untuk production

---

## SOLUSI 3: Setup Script (IMPLEMENTED)

Script `scripts/setup.sh` yang:
1. ✅ Check dependencies (instant if cached)
2. ✅ Verify corpus file
3. ✅ Setup .env
4. ✅ Check SBERT cache status
5. ✅ Run npm install hanya jika perlu

**Usage:**
```bash
# Setelah restart VS Code
bash scripts/setup.sh

# Output:
# ✓ Python 3.12.1
# ✓ All required packages installed
# ✓ Corpus file found (397M)
# ✓ .env configured
# ✓ SBERT model cached
# ✓ node_modules exists

# Setup time: ~30 detik
```

---

## LENGKAP WORKFLOW SETELAH RESTART

### Scenario 1: Normal Restart (Ideal Path)

```bash
# 1. VS Code restart
# 2. Terminal buka
# 3. Run quick setup (MANDATORY)
bash scripts/setup.sh
# Output: ✓ All checks passed (30 detik)

# 4. Start backend (INSTANT, no model download)
cd backend
python -m uvicorn main:app --reload
# Model load: <5 detik
# Server ready: ~10 detik total

# 5. Start frontend (no npm install)
cd frontend
npm start
# npm cache hit: <2 detik
# Dev server ready: ~5 detik

# 6. Browser
# http://localhost:3000
# ✓ System fully operational: <30 detik dari startup
```

### Scenario 2: First Time Setup (One-time Pain)

```bash
# 1. Clone & setup
bash scripts/setup.sh
# Missing packages: install from requirements.txt (~1 min)
# ✓ Dependencies installed

# 2. Start backend
cd backend && python main.py
# Missing SBERT model: download from Huggingface (~3 min)
# ✓ Model cached

# 3. Health check
curl http://localhost:8000/health
# ✓ System ready

# 4. Start frontend
cd frontend && npm start
# ✓ Dev server ready

# Total first time: ~5-8 menit (acceptable one-time setup)
```

### Scenario 3: After Restart (Optimal)

```bash
# 1. Setup check (pre-flight)
bash scripts/setup.sh
# ✓ All cached: <30 detik

# 2. Run backend
cd backend && python main.py
# Model load dari cache: <5 detik
# ✓ Backend ready

# 3. Run frontend
cd frontend && npm start
# npm cache hit: <5 detik
# ✓ Frontend ready

# 4. Access system
# http://localhost:3000
# ✓ Full system: <30 detik total ⚡
```

---

## TECHNICAL DETAILS

### 1. SBERT Cache Location

```bash
# Huggingface default cache
~/.cache/huggingface/hub/

# Model path
~/.cache/huggingface/hub/models--sentence-transformers--paraphrase-multilingual-mpnet-base-v2/
├── refs/main/
├── snapshots/
│   └── <hash>/
│       ├── config.json
│       ├── pytorch_model.bin (~440 MB)
│       ├── tokenizer.json
│       └── ...
└── blobs/

# Size: ~440 MB
# Persistence: ✓ Codespace storage (NOT container-ephemeral)
# Auto-cache: ✓ Yes (huggingface library handles)
```

### 2. npm Cache

```bash
# npm cache location
~/.npm/

# npm cache structure
~/.npm/_cacache/
├── content-v2/
├── index-v5/
└── ... (indexed binary storage)

# Cache behavior
npm install   # Checks cache, downloads missing
npm ci         # Cleaner, more cache-friendly
npm cache ls  # List cache contents
npm cache clean --force  # Clear cache if needed
```

### 3. Environment Setup

**Current state:**
```bash
# backend/.env (already configured)
GOOGLE_API_KEY=...
GOOGLE_CSE_ID=...
CORPUS_PKL_PATH=data/corpus.pkl

# Python venv (NOT used, global Python)
# Global python packages: ✓ Installed and cached

# Node environment
NODE_HOME=/usr/local/share/nvm/versions/node/v24.11.1
npm cache: ~/.npm/
node_modules cache: frontend/node_modules/ (exists)
```

---

## BEST PRACTICES MOVING FORWARD

### ✅ DO:

1. **Run setup.sh setelah restart:**
   ```bash
   bash scripts/setup.sh
   ```

2. **Use `npm ci` untuk deterministic install:**
   ```bash
   npm ci  # lebih cepat dari npm install
   ```

3. **Check cache status occasionally:**
   ```bash
   ls -lh ~/.cache/huggingface/hub/
   npm cache ls | wc -l  # should have many entries
   ```

4. **Commit package-lock.json:**
   ```bash
   git add frontend/package-lock.json
   ```

### ❌ DON'T:

1. **Clear cache manually** (unless troubleshooting)
   ```bash
   # ❌ DON'T: npm cache clean --force
   # Ini akan delete cache dan force re-download
   ```

2. **Commit node_modules** (unless absolutely needed)
   ```bash
   # ❌ node_modules/ should remain in .gitignore
   ```

3. **Use pip install untuk individual packages**
   ```bash
   # ✅ DO: pip install -r backend/requirements.txt
   # ❌ DON'T: pip install fastapi (tidak tracked)
   ```

---

## Testing Cache Effectiveness

### Test 1: Verify SBERT Cache Hit

```bash
# First run
time python backend/main.py
# Output: ~10-15 detik (includes model loading)

# Stop server (Ctrl+C)

# Second run (cache should hit)
time python backend/main.py
# Output: ~2-5 detik (model from cache) ✓
```

### Test 2: Verify npm Cache

```bash
# Remove node_modules
rm -rf frontend/node_modules

# Install from cache (should be faster)
time npm ci
# First time: 2-3 menit
# Second time: <30 detik (cache hit)
```

### Test 3: Full Restart Simulation

```bash
# Simulate restart
bash scripts/setup.sh
# Should complete: <30 detik

# Time full startup
time (cd backend && python main.py & \
      sleep 5 && \
      cd frontend && npm start & \
      wait)
# Total: <30 detik (both services)
```

---

## Troubleshooting Cache Issues

### Issue 1: Model keeps re-downloading

```bash
# Check cache
ls ~/.cache/huggingface/hub/
# If empty, cache corrupted

# Solution: Re-download once
rm -rf ~/.cache/huggingface/
python backend/main.py
# Will re-download and cache again
```

### Issue 2: npm install always slow

```bash
# Check npm cache
npm cache verify
# Output should show "verified cache"

# Clear and rebuild cache if corrupted
npm cache clean --force
npm install
```

### Issue 3: Disk space issue

```bash
# Check space
du -sh ~/.cache/huggingface/  # Model cache
du -sh ~/.npm/                # npm cache
du -sh frontend/node_modules/ # node_modules

# If >10GB, safe to clean:
npm cache clean --force  # npm cache only
# Do NOT delete huggingface cache (re-download takes time)
```

---

## Summary

| Item | Before | After | Improvement |
|------|--------|-------|-------------|
| Model download | Every restart | Once, then cached | Save 3 min/restart |
| npm install | Every restart | From cache | Save 2 min/restart |
| Setup time | ~5 menit | ~30 detik | 10x faster |
| Backend startup | ~15 detik | <5 detik | 3x faster |
| Frontend startup | ~10 detik | <5 detik | 2x faster |
| **Total restart time** | **~5-8 min** | **~30 sec** | **10x faster** |

---

## Files Updated

- `scripts/setup.sh` - Quick setup script dengan cache checks
- `backend/requirements.txt` - Dependencies (unchanged, already optimized)
- `frontend/package.json` - Dependencies (unchanged, uses npm cache)
- `backend/.env` - Configuration (unchanged, persists across restarts)

---

## Next Steps

1. ✅ Run setup script pertama kali:
   ```bash
   bash scripts/setup.sh
   ```

2. ✅ First run backend (model akan cache):
   ```bash
   cd backend && python main.py
   # Wait untuk model download: ~3 menit
   ```

3. ✅ Test restart behavior:
   - Close VS Code
   - Reopen
   - Run `bash scripts/setup.sh` again
   - Verify ~30 detik instead of 5 menit

4. ✅ Commit setup script:
   ```bash
   git add scripts/setup.sh
   git commit -m "feat: add setup.sh for quick restart recovery"
   git push upstream main
   ```
