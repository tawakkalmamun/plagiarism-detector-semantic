"""
Core Module untuk Sistem Deteksi Plagiarisme Semantik
"""

from .plagiarism_detector import PlagiarismDetector
from .pdf_processor import PDFProcessor

__version__ = "1.0.0"
__all__ = ["PlagiarismDetector", "PDFProcessor"]
