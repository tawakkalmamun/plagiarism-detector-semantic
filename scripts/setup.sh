#!/bin/bash
# setup.sh - Quick Setup Script untuk Restart Codespace
# Jalankan: bash scripts/setup.sh
# Waktu: ~30 detik (tanpa download model atau npm install)

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "╔════════════════════════════════════════════════════╗"
echo "║  PLAGIARISM DETECTOR - Quick Setup Script          ║"
echo "║  Version 1.0                                       ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================
# 1. CHECK PYTHON & DEPENDENCIES
# ============================================================
echo -e "${BLUE}[1/5] Checking Python & Dependencies...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3 not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"

# Check critical packages
REQUIRED_PACKAGES=("fastapi" "pdfplumber" "sentence_transformers" "torch" "loguru")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import ${package}" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠ Missing packages: ${MISSING_PACKAGES[*]}${NC}"
    echo "  Installing dependencies from requirements.txt..."
    pip install -q -r backend/requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ All required packages installed${NC}"
fi

# ============================================================
# 2. CHECK CORPUS FILE
# ============================================================
echo ""
echo -e "${BLUE}[2/5] Checking Corpus File...${NC}"

if [ ! -f "data/corpus.pkl" ]; then
    echo -e "${RED}✗ Corpus file missing: data/corpus.pkl${NC}"
    echo "  Please run: python backend/build_corpus.py"
    exit 1
fi

CORPUS_SIZE=$(ls -lh data/corpus.pkl | awk '{print $5}')
CORPUS_SEGMENTS=$(python3 -c "import pickle; data=pickle.load(open('data/corpus.pkl','rb')); print(len(data.get('segments', [])))" 2>/dev/null || echo "N/A")
echo -e "${GREEN}✓ Corpus file found (${CORPUS_SIZE})${NC}"
echo "  Segments: ${CORPUS_SEGMENTS}"

# ============================================================
# 3. CHECK & SETUP .ENV
# ============================================================
echo ""
echo -e "${BLUE}[3/5] Checking Configuration (.env)...${NC}"

if [ ! -f "backend/.env" ]; then
    echo -e "${RED}✗ .env file missing${NC}"
    echo "  Creating .env from template..."
    cat > backend/.env << 'EOF'
# Google Custom Search Engine Configuration
GOOGLE_API_KEY=your_api_key_here
GOOGLE_CSE_ID=your_cse_id_here

# Corpus Configuration
CORPUS_PKL_PATH=data/corpus.pkl
EOF
    echo -e "${YELLOW}⚠ Please update backend/.env with your Google CSE credentials${NC}"
else
    # Validate .env
    if grep -q "GOOGLE_API_KEY=" backend/.env && grep -q "GOOGLE_CSE_ID=" backend/.env; then
        echo -e "${GREEN}✓ .env configured${NC}"
    else
        echo -e "${YELLOW}⚠ .env exists but may need Google CSE credentials${NC}"
    fi
fi

# ============================================================
# 4. CHECK NODE & FRONTEND
# ============================================================
echo ""
echo -e "${BLUE}[4/5] Checking Node.js & Frontend...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ Node ${NODE_VERSION} & npm ${NPM_VERSION}${NC}"

if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠ node_modules not found, installing...${NC}"
    cd frontend
    npm install --silent --no-progress 2>&1 | tail -1
    cd ..
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ node_modules exists${NC}"
fi

# ============================================================
# 5. CHECK SBERT MODEL CACHE
# ============================================================
echo ""
echo -e "${BLUE}[5/5] Checking SBERT Model Cache...${NC}"

SBERT_CACHE="${HOME}/.cache/huggingface/hub/models--sentence-transformers--paraphrase-multilingual-mpnet-base-v2"

if [ -d "$SBERT_CACHE" ]; then
    CACHE_SIZE=$(du -sh "$SBERT_CACHE" 2>/dev/null | cut -f1)
    echo -e "${GREEN}✓ SBERT model cached (${CACHE_SIZE})${NC}"
else
    echo -e "${YELLOW}⚠ SBERT model not cached yet${NC}"
    echo "  It will auto-download on first backend run (~2-3 min)"
fi

# ============================================================
# SUMMARY
# ============================================================
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║  Setup Complete!                                   ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Ready to run:${NC}"
echo ""
echo "  Terminal 1 - Backend:"
echo "  $ cd backend && python -m uvicorn main:app --reload"
echo ""
echo "  Terminal 2 - Frontend:"
echo "  $ cd frontend && npm start"
echo ""
echo "  Browser:"
echo "  $ open http://localhost:3000"
echo ""
echo -e "${BLUE}Tips:${NC}"
echo "  • Run this script again anytime: bash scripts/setup.sh"
echo "  • Check logs: tail -f logs/api.out"
echo "  • Test health: curl http://localhost:8000/health"
echo ""
