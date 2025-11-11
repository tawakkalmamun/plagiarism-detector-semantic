"""
PDF Processing Module - Simplified Version
Stub version untuk testing tanpa dependencies berat
"""

from typing import Optional, Dict
from loguru import logger
import re


class PDFProcessor:
    """
    Kelas untuk memproses file PDF dan mengekstrak teks - Simplified Version
    """
    
    def __init__(self, use_pdfplumber: bool = True):
        """
        Initialize PDF Processor - Simplified Version
        """
        self.use_pdfplumber = use_pdfplumber
        logger.info("PDFProcessor initialized (simplified mode)")
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF - Simplified version
        """
        logger.info(f"Extracting text from {pdf_path} (simplified mode)")
        
        # Return mock text for testing
        return "Sample PDF text content for testing purposes."
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """
        Extract text menggunakan PyPDF2 - Simplified version
        """
        return self.extract_text(pdf_path)
    
    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """
        Extract text menggunakan pdfplumber - Simplified version
        """
        return self.extract_text(pdf_path)
    
    def clean_text(self, text: str) -> str:
        """
        Bersihkan dan normalisasi teks
        """
        if not text:
            return ""
        
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]]', '', text)
        
        # Strip and return
        return text.strip()
    
    def clean_extracted_text(self, text: str) -> str:
        """
        Bersihkan teks yang telah diekstrak dari PDF - Simplified version
        """
        if not text:
            return ""
        
        # Remove multiple spaces and normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers patterns
        text = re.sub(r'\n\d+\n', ' ', text)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Clean up punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]]', ' ', text)
        
        # Remove extra whitespaces again
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validasi apakah file adalah PDF yang valid - Simplified version
        """
        try:
            import os
            if not os.path.exists(pdf_path):
                logger.error(f"File tidak ditemukan: {pdf_path}")
                return False
            
            # Check file extension
            if not pdf_path.lower().endswith('.pdf'):
                logger.error(f"Bukan file PDF: {pdf_path}")
                return False
            
            # Check file size (minimal 1KB)
            file_size = os.path.getsize(pdf_path)
            if file_size < 1024:
                logger.error(f"File terlalu kecil: {file_size} bytes")
                return False
            
            logger.info(f"PDF validation passed: {pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating PDF: {e}")
            return False
    
    def extract_abstract(self, pdf_path: str) -> str:
        """
        Extract abstract dari PDF - Simplified version
        """
        logger.info(f"Extracting abstract from {pdf_path} (simplified mode)")
        
        # Return mock abstract for testing
        return "This is a sample abstract extracted from the PDF document for testing purposes. It contains the main points and summary of the research."
    
    def get_metadata(self, pdf_path: str) -> Dict:
        """
        Ambil metadata PDF - Simplified version
        """
        logger.info(f"Getting metadata from {pdf_path} (simplified mode)")
        
        return {
            "title": "Sample Document",
            "author": "Unknown",
            "subject": "",
            "creator": "Simplified PDF Processor",
            "pages": 1,
            "file_size": 0
        }
