"""
FastAPI Main Application
API Server untuk Sistem Deteksi Plagiarisme Semantik
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import shutil
import uuid
from datetime import datetime
from loguru import logger
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from the backend directory
load_dotenv()

from core.plagiarism_detector import PlagiarismDetector
from core.pdf_processor_full import PDFProcessor

# Configure logger
logger.add(
    "logs/app_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO"
)

# Initialize FastAPI
app = FastAPI(
    title="Plagiarism Detection API",
    description="API untuk Deteksi Plagiarisme Semantik menggunakan Google CSE dan Sentence-BERT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dalam production, ganti dengan domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Initialize processors
pdf_processor = PDFProcessor(use_pdfplumber=True)
plagiarism_detector = PlagiarismDetector(
    similarity_threshold=0.75,
    segment_size=25,
    overlap=5
)


# Pydantic Models
class DetectionRequest(BaseModel):
    """Request model untuk deteksi plagiarisme"""
    threshold: Optional[float] = Field(0.75, ge=0.0, le=1.0, description="Similarity threshold")
    use_search: Optional[bool] = Field(True, description="Use Google search")
    extract_abstract: Optional[bool] = Field(False, description="Only analyze abstract section")


class DetectionResponse(BaseModel):
    """Response model untuk hasil deteksi"""
    task_id: str
    filename: str
    status: str
    total_segments: int
    plagiarized_segments: int
    original_segments: int
    plagiarism_percentage: float
    avg_similarity: float
    threshold_used: float
    processing_time: float
    timestamp: str
    details: List[dict]


class HealthResponse(BaseModel):
    """Response untuk health check"""
    status: str
    timestamp: str
    services: dict


# In-memory task storage (dalam production gunakan database)
tasks_storage = {}


# Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Plagiarism Detection API",
        "version": "1.0.0",
        "description": "Deteksi Plagiarisme Semantik untuk Skripsi Mahasiswa",
        "documentation": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    
    # Check services
    services = {
        "api": "running",
        "sbert_model": "loaded" if plagiarism_detector.model else "not loaded",
        "google_cse": "available" if plagiarism_detector.search_service else "not configured"
    }
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": services
    }


@app.post("/api/detect", tags=["Detection"])
async def detect_plagiarism(
    file: UploadFile = File(..., description="PDF file to analyze"),
    threshold: float = Form(0.75, ge=0.0, le=1.0, description="Similarity threshold"),
    use_search: bool = Form(True, description="Use Google search"),
    extract_abstract: bool = Form(False, description="Only analyze abstract"),
    add_to_corpus: bool = Form(False, description="Tambahkan teks ke local corpus"),
    use_local_corpus: bool = Form(True, description="Gunakan local corpus untuk pencarian internal"),
    chapters_only: bool = Form(False, description="Hanya ambil konten Bab 1-5 (skip sampul, kata pengantar, dll)"),
    start_chapter: int = Form(1, ge=1, le=10, description="Bab awal (default: 1)"),
    end_chapter: int = Form(5, ge=1, le=10, description="Bab akhir (default: 5)")
):
    """
    Endpoint utama untuk deteksi plagiarisme
    
    Args:
        file: PDF file upload
        threshold: Threshold kemiripan (0.0 - 1.0)
        use_search: Gunakan Google search atau tidak
        extract_abstract: Hanya analisis abstrak atau full text
        chapters_only: Filter hanya konten Bab tertentu (skip bagian awal)
        start_chapter: Nomor bab awal untuk dianalisis
        end_chapter: Nomor bab akhir untuk dianalisis
        
    Returns:
        Detection result dengan detail per segment
    """
    
    task_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    logger.info(f"New detection task: {task_id} for file: {file.filename}")
    
    # Validate file type
    if not (file.filename.endswith('.pdf') or file.filename.endswith('.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
    
    # Save uploaded file
    upload_path = f"uploads/{task_id}_{file.filename}"
    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved: {upload_path}")
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving file")
    
    # Process PDF
    try:
        # Validate PDF (TEMP: DISABLED for debugging)
        # if not pdf_processor.validate_pdf(upload_path):
        #     raise HTTPException(status_code=400, detail="Invalid PDF file")
        logger.info(f"Skipping PDF validation for debugging, processing file directly")
        
        # Extract text
        if file.filename.endswith('.txt'):
            # Handle text files
            try:
                with open(upload_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                # Try with different encoding if UTF-8 fails
                with open(upload_path, 'r', encoding='latin-1') as f:
                    text = f.read()
        else:
            # Handle PDF files
            if extract_abstract:
                text = pdf_processor.extract_abstract(upload_path)
                if not text:
                    raise HTTPException(status_code=400, detail="Abstract not found in PDF")
            elif chapters_only:
                # Extract hanya konten Bab tertentu (skip sampul, kata pengantar, dll)
                text = pdf_processor.extract_chapters_only(upload_path, start_chapter, end_chapter)
                logger.info(f"Extracted chapters {start_chapter}-{end_chapter}: {len(text)} chars")
            else:
                text = pdf_processor.extract_text(upload_path)
        
        # Clean text
        text = pdf_processor.clean_extracted_text(text)
        
        logger.info(f"Text extracted: {len(text)} characters")
        
        # Update detector threshold
        plagiarism_detector.similarity_threshold = threshold
        
        # Detect plagiarism (TEMP: force use_search=False for debugging)
        logger.info(f"use_search parameter: {use_search}, forcing to False for testing")
        result = plagiarism_detector.detect_plagiarism(
            text,
            use_search=False,
            use_local_corpus=use_local_corpus,
            add_to_corpus=add_to_corpus,
            corpus_source_id=task_id
        )

        # Normalisasi label (Indonesia -> English for consistency)
        for item in result.get('details', []):
            if item.get('label') == 'Plagiat':
                item['label'] = 'PLAGIARIZED'
            elif item.get('label') == 'Original':
                item['label'] = 'ORIGINAL'
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Prepare response
        response = {
            "task_id": task_id,
            "filename": file.filename,
            "status": "completed",
            "total_segments": result['total_segments'],
            "plagiarized_segments": result['plagiarized_segments'],
            "original_segments": result['original_segments'],
            "plagiarism_percentage": result['plagiarism_percentage'],
            "avg_similarity": result['avg_similarity'],
            "threshold_used": result['threshold_used'],
            "processing_time": round(processing_time, 2),
            "timestamp": end_time.isoformat(),
            "details": result['details']
        }
        
        # Store result
        tasks_storage[task_id] = response
        
        # Save to CSV
        csv_path = f"results/{task_id}_results.csv"
        save_results_to_csv(result['details'], csv_path, file.filename)
        
        logger.info(f"Detection completed: {task_id} ({processing_time:.2f}s)")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        # Cleanup uploaded file
        try:
            if os.path.exists(upload_path):
                os.remove(upload_path)
                logger.info(f"Cleanup: {upload_path}")
        except:
            pass


@app.get("/api/result/{task_id}", tags=["Detection"])
async def get_result(task_id: str):
    """
    Mendapatkan hasil deteksi berdasarkan task_id
    
    Args:
        task_id: ID task yang ingin dicari
        
    Returns:
        Detection result
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks_storage[task_id]


@app.get("/api/download/{task_id}", tags=["Detection"])
async def download_result(task_id: str):
    """
    Download hasil deteksi dalam format CSV
    
    Args:
        task_id: ID task
        
    Returns:
        CSV file
    """
    csv_path = f"results/{task_id}_results.csv"
    
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(
        path=csv_path,
        filename=f"plagiarism_report_{task_id}.csv",
        media_type="text/csv"
    )


@app.post("/api/detect-text", tags=["Detection"])
async def detect_text(
    text: str = Form(..., description="Text to analyze"),
    threshold: float = Form(0.75, ge=0.0, le=1.0),
    use_search: bool = Form(True),
    add_to_corpus: bool = Form(False),
    use_local_corpus: bool = Form(True)
):
    """
    Deteksi plagiarisme dari raw text (bukan PDF)
    
    Args:
        text: Teks yang akan dianalisis
        threshold: Similarity threshold
        use_search: Gunakan Google search
        
    Returns:
        Detection result
    """
    task_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    logger.info(f"New text detection task: {task_id}")
    
    if len(text) < 50:
        raise HTTPException(status_code=400, detail="Text too short (minimum 50 characters)")
    
    try:
        # Update threshold
        plagiarism_detector.similarity_threshold = threshold
        
        # Detect
        result = plagiarism_detector.detect_plagiarism(
            text,
            use_search=use_search,
            use_local_corpus=use_local_corpus,
            add_to_corpus=add_to_corpus,
            corpus_source_id=task_id
        )

        # Normalisasi label
        for item in result.get('details', []):
            if item.get('label') == 'Plagiat':
                item['label'] = 'PLAGIARIZED'
            elif item.get('label') == 'Original':
                item['label'] = 'ORIGINAL'
        
        # Processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Response
        response = {
            "task_id": task_id,
            "filename": "text_input",
            "status": "completed",
            "total_segments": result['total_segments'],
            "plagiarized_segments": result['plagiarized_segments'],
            "original_segments": result['original_segments'],
            "plagiarism_percentage": result['plagiarism_percentage'],
            "avg_similarity": result['avg_similarity'],
            "threshold_used": result['threshold_used'],
            "processing_time": round(processing_time, 2),
            "timestamp": end_time.isoformat(),
            "details": result['details']
        }
        
        tasks_storage[task_id] = response
        
        return response
        
    except Exception as e:
        logger.error(f"Error detecting text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/segment", tags=["Debug"])
async def segment_only(
    text: Optional[str] = Form(None, description="Raw text to segment"),
    file: Optional[UploadFile] = File(None, description="PDF/TXT file to segment"),
    extract_abstract: bool = Form(False),
    add_to_corpus: bool = Form(False),
    corpus_label: Optional[str] = Form(None)
):
    """Endpoint untuk hanya mengembalikan segmentasi tanpa deteksi plagiarisme."""
    task_id = str(uuid.uuid4())
    content = None
    upload_path = None
    try:
        if file is not None:
            if not (file.filename.endswith('.pdf') or file.filename.endswith('.txt')):
                raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
            upload_path = f"uploads/{task_id}_{file.filename}"
            with open(upload_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            if file.filename.endswith('.txt'):
                with open(upload_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            else:
                if extract_abstract:
                    content = pdf_processor.extract_abstract(upload_path)
                else:
                    content = pdf_processor.extract_text(upload_path)
        elif text is not None:
            content = text
        else:
            raise HTTPException(status_code=400, detail="Provide either text or file")

        content = pdf_processor.clean_extracted_text(content)
        segments = plagiarism_detector.segment_text(content)
        if add_to_corpus:
            plagiarism_detector.add_to_corpus(content, source_id=corpus_label or task_id)
        return {
            'task_id': task_id,
            'total_segments': len(segments),
            'segments': segments,
            'added_to_corpus': add_to_corpus,
            'corpus_size': len(plagiarism_detector.local_corpus)
        }
    except Exception as e:
        logger.error(f"Segment endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            if upload_path and os.path.exists(upload_path):
                os.remove(upload_path)
        except:
            pass


@app.get("/api/tasks", tags=["Detection"])
async def list_tasks():
    """
    List semua detection tasks yang tersimpan
    
    Returns:
        List of tasks
    """
    tasks = []
    for task_id, result in tasks_storage.items():
        tasks.append({
            "task_id": task_id,
            "filename": result.get("filename"),
            "timestamp": result.get("timestamp"),
            "plagiarism_percentage": result.get("plagiarism_percentage"),
            "status": result.get("status")
        })
    
    return {"total_tasks": len(tasks), "tasks": tasks}


@app.delete("/api/task/{task_id}", tags=["Detection"])
async def delete_task(task_id: str):
    """
    Hapus task dan hasil deteksi
    
    Args:
        task_id: ID task yang akan dihapus
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Remove from storage
    del tasks_storage[task_id]
    
    # Remove CSV file
    csv_path = f"results/{task_id}_results.csv"
    if os.path.exists(csv_path):
        os.remove(csv_path)
    
    return {"message": "Task deleted successfully", "task_id": task_id}


@app.post("/api/corpus/build", tags=["Corpus Management"])
async def build_corpus(
    folder_path: str = Form("uploads/corpus_skripsi", description="Path ke folder berisi PDF/TXT corpus"),
    file_extension: str = Form(".pdf", description="Extension file (.pdf atau .txt)"),
    clear_existing: bool = Form(False, description="Hapus corpus yang ada sebelum build")
):
    """
    Build local corpus dari folder berisi file skripsi lama (PDF/TXT).
    Corpus ini akan digunakan untuk pembanding deteksi plagiarisme.
    
    Args:
        folder_path: Path folder berisi file corpus
        file_extension: .pdf atau .txt
        clear_existing: Hapus corpus lama sebelum build baru
        
    Returns:
        Result build corpus
    """
    try:
        # Clear existing corpus jika diminta
        if clear_existing:
            cleared = plagiarism_detector.clear_corpus()
            logger.info(f"Cleared {cleared} existing corpus segments")
        
        # Build corpus dari folder
        result = plagiarism_detector.build_corpus_from_folder(folder_path, file_extension)
        
        return {
            "success": result['success'],
            "message": result['message'],
            "files_processed": result['files_processed'],
            "total_segments": result['total_segments'],
            "corpus_size": result['corpus_size'],
            "errors": result['errors'],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error building corpus: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/corpus/info", tags=["Corpus Management"])
async def get_corpus_info():
    """
    Dapatkan informasi tentang corpus lokal saat ini.
    
    Returns:
        Info corpus: size, sources, dll
    """
    try:
        info = plagiarism_detector.get_corpus_info()
        return {
            "corpus_size": info['size'],
            "sources": info['sources'],
            "is_empty": info['empty'],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting corpus info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/corpus/clear", tags=["Corpus Management"])
async def clear_corpus():
    """
    Hapus semua corpus lokal.
    
    Returns:
        Jumlah segment yang dihapus
    """
    try:
        cleared = plagiarism_detector.clear_corpus()
        return {
            "success": True,
            "message": f"Cleared {cleared} segments from corpus",
            "segments_cleared": cleared,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing corpus: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/corpus/save", tags=["Corpus Management"])
async def save_corpus(path: str = Form("data/corpus.pkl")):
    """Simpan corpus lokal ke file pickle."""
    try:
        info = plagiarism_detector.save_corpus(path)
        return {
            'success': info['success'],
            'segments': info['segments'],
            'path': info['path'],
            'time_sec': info['time_sec'],
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error saving corpus: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/corpus/load", tags=["Corpus Management"])
async def load_corpus(path: str = Form("data/corpus.pkl")):
    """Muat corpus lokal dari file pickle."""
    try:
        info = plagiarism_detector.load_corpus(path)
        if not info['success']:
            raise HTTPException(status_code=404, detail=info.get('message', 'Load failed'))
        return {
            'success': True,
            'segments': info['segments'],
            'path': info['path'],
            'format_version': info['format_version'],
            'time_sec': info['time_sec'],
            'timestamp': datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading corpus: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper Functions
def save_results_to_csv(details: List[dict], csv_path: str, filename: str):
    """
    Menyimpan hasil deteksi ke CSV file
    
    Args:
        details: List hasil deteksi per segment
        csv_path: Path untuk save CSV
        filename: Nama file asli
    """
    try:
        # Prepare data
        data = []
        for item in details:
            data.append({
                'segment_id': item['segment_id'],
                'segment_text': item['segment_text'],
                'word_count': item['word_count'],
                'best_match': item['best_match'] or '',
                'similarity_score': item['similarity_score'],
                'label': item['label'],
                'source_url': item['source_url'] or '',
                'source_title': item['source_title'] or ''
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        logger.info(f"Results saved to CSV: {csv_path}")
        
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Actions on startup"""
    logger.info("=" * 50)
    logger.info("Plagiarism Detection API Starting...")
    logger.info("=" * 50)
    logger.info(f"SBERT Model: Loaded")
    logger.info(f"Google CSE: {'Configured' if plagiarism_detector.search_service else 'Not Configured'}")
    logger.info("API Ready!")
    # Auto load corpus if exists
    default_corpus_path = os.getenv("CORPUS_PKL_PATH", "data/corpus.pkl")
    if os.path.exists(default_corpus_path):
        try:
            info = plagiarism_detector.load_corpus(default_corpus_path)
            logger.info(f"Auto-loaded corpus: {info['segments']} segments from {default_corpus_path}")
        except Exception as e:
            logger.error(f"Failed auto-load corpus: {e}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Actions on shutdown"""
    logger.info("API Shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
