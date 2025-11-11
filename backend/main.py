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
from core.pdf_processor import PDFProcessor

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
    extract_abstract: bool = Form(False, description="Only analyze abstract")
):
    """
    Endpoint utama untuk deteksi plagiarisme
    
    Args:
        file: PDF file upload
        threshold: Threshold kemiripan (0.0 - 1.0)
        use_search: Gunakan Google search atau tidak
        extract_abstract: Hanya analisis abstrak atau full text
        
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
        # Validate PDF
        if not pdf_processor.validate_pdf(upload_path):
            raise HTTPException(status_code=400, detail="Invalid PDF file")
        
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
            else:
                text = pdf_processor.extract_text(upload_path)
        
        # Clean text
        text = pdf_processor.clean_extracted_text(text)
        
        logger.info(f"Text extracted: {len(text)} characters")
        
        # Update detector threshold
        plagiarism_detector.similarity_threshold = threshold
        
        # Detect plagiarism
        result = plagiarism_detector.detect_plagiarism(text, use_search=use_search)
        
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
    use_search: bool = Form(True)
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
        result = plagiarism_detector.detect_plagiarism(text, use_search=use_search)
        
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
