"""
PDF Processing Module
Extract text from PDF files for plagiarism detection
"""

import PyPDF2
import pdfplumber
from typing import Optional, Dict
from loguru import logger
import re
# OCR dinonaktifkan (diminta user), tidak lagi diimpor maupun dipakai.
_ocr_available = False


class PDFProcessor:
    """
    Kelas untuk memproses file PDF dan mengekstrak teks
    """
    
    def __init__(self, use_pdfplumber: bool = True):
        """
        Initialize PDF Processor
        
        Args:
            use_pdfplumber: Gunakan pdfplumber (lebih akurat) atau PyPDF2
        """
        self.use_pdfplumber = use_pdfplumber
        logger.info(f"PDFProcessor initialized with {'pdfplumber' if use_pdfplumber else 'PyPDF2'}")
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """
        Extract text menggunakan PyPDF2
        
        Args:
            pdf_path: Path ke file PDF
            
        Returns:
            Extracted text
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                logger.info(f"Extracting text from {num_pages} pages using PyPDF2")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            raise
    
    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """
        Extract text menggunakan pdfplumber (lebih akurat)
        
        Args:
            pdf_path: Path ke file PDF
            
        Returns:
            Extracted text
        """
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
                
                logger.info(f"Extracting text from {num_pages} pages using pdfplumber")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        logger.debug(f"Page {page_num}: {len(page_text)} characters extracted")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber: {e}")
            raise
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text dari PDF dengan fallback mechanism
        
        Args:
            pdf_path: Path ke file PDF
            
        Returns:
            Extracted text
        """
        text = ""
        try:
            if self.use_pdfplumber:
                text = self.extract_text_pdfplumber(pdf_path)
            else:
                text = self.extract_text_pypdf2(pdf_path)
        except Exception as e:
            logger.warning(f"Primary extraction failed: {e}")
        
        # Fallback jika text kosong atau gagal (method lain)
        if not text or len(text.strip()) < 100:
            logger.warning(f"Primary extraction returned insufficient text ({len(text)} chars). Trying alternative PDF method...")
            alt_text = ''
            try:
                if self.use_pdfplumber:
                    alt_text = self.extract_text_pypdf2(pdf_path)
                else:
                    alt_text = self.extract_text_pdfplumber(pdf_path)
                if alt_text and len(alt_text.strip()) > len(text.strip()):
                    text = alt_text
                logger.info(f"Alternative PDF method extracted {len(alt_text)} chars (selected {len(text)}).")
            except Exception as e2:
                logger.error(f"Alternative PDF method failed: {e2}")

        if not text or len(text.strip()) < 30:
            logger.warning("Final extracted text very short (<30 chars). Document may be scanned or empty (OCR disabled).")
        
        return text
    
    def extract_chapters_only(self, pdf_path: str, start_chapter: int = 1, end_chapter: int = 5) -> str:
        """
        Extract hanya konten dari Bab tertentu (skip sampul, kata pengantar, daftar isi)
        
        Args:
            pdf_path: Path ke file PDF
            start_chapter: Bab awal (default: 1)
            end_chapter: Bab akhir (default: 5)
            
        Returns:
            Text dari bab yang diminta saja
        """
        try:
            full_text = self.extract_text(pdf_path)

            # Hilangkan blok "Daftar Isi/Tabel/Gambar/Lampiran" agar tidak menangkap baris BAB di daftar isi
            work_text = full_text
            try:
                toc_like_sections = [
                    r"(?im)^\s*DAFTAR\s+ISI\b",
                    r"(?im)^\s*DAFTAR\s+TABEL\b",
                    r"(?im)^\s*DAFTAR\s+GAMBAR\b",
                    r"(?im)^\s*DAFTAR\s+LAMPIRAN\b",
                ]
                toc_end_guard = r"(?im)^(\s*ABSTRAK\b|\s*ABSTRACT\b|\s*BAB\s+[IVX]+\b|\s*BAB\s+\d+\b)"
                for sec in toc_like_sections:
                    pattern = re.compile(sec + r".*?" + toc_end_guard, re.DOTALL | re.IGNORECASE | re.MULTILINE)
                    work_text, n = re.subn(pattern, "", work_text)
                    if n:
                        logger.info(f"Removed TOC-like section using pattern: {sec} (occurrences: {n})")
            except Exception as _:
                # Abaikan jika pembersihan TOC gagal, lanjut dengan full_text
                work_text = full_text
            
            # Pattern untuk mendeteksi BAB (berbagai format)
            # Contoh: "BAB I", "BAB 1", "BAB I PENDAHULUAN", "BAB 1 PENDAHULUAN"
            bab_patterns = []
            
            # Generate pattern untuk semua bab dari start sampai end
            for i in range(start_chapter, end_chapter + 2):  # +2 untuk deteksi batas akhir
                # Romawi
                romawi = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
                if i <= len(romawi):
                    # BAB I, Bab I, bab I
                    bab_patterns.append(rf'(?i)^[\s]*BAB\s+{romawi[i-1]}\b')
                # Angka arab
                bab_patterns.append(rf'(?i)^[\s]*BAB\s+{i}\b')
            
            # Cari posisi setiap bab
            bab_positions = []
            for pattern in bab_patterns:
                for match in re.finditer(pattern, work_text, re.MULTILINE):
                    # Extract nomor bab dari match
                    bab_text = match.group(0).upper()

                    # Skip baris BAB yang berasal dari daftar isi (memiliki titik-titik pemimpin dan nomor halaman)
                    # Ambil teks satu baris penuh tempat match terjadi
                    line_start = work_text.rfind('\n', 0, match.start()) + 1
                    line_end = work_text.find('\n', match.start())
                    if line_end == -1:
                        line_end = len(work_text)
                    whole_line = work_text[line_start:line_end]
                    if re.search(r"\.{3,}\s*\d+\s*$", whole_line):
                        # Contoh: "BAB I PENDAHULUAN..................... 1" → skip (kemungkinan dari daftar isi)
                        continue
                    
                    # Deteksi nomor bab
                    romawi_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
                    bab_num = None
                    
                    # Cek romawi
                    for rom, num in romawi_map.items():
                        if f' {rom}' in bab_text or f'{rom} ' in bab_text:
                            bab_num = num
                            break
                    
                    # Cek angka arab
                    if not bab_num:
                        match_digit = re.search(r'\d+', bab_text)
                        if match_digit:
                            bab_num = int(match_digit.group())
                    
                    if bab_num:
                        bab_positions.append({
                            'number': bab_num,
                            'start': match.start(),
                            'end': match.end()
                        })
            
            # Sort berdasarkan posisi
            bab_positions.sort(key=lambda x: x['start'])
            
            # Filter hanya bab yang diminta
            filtered_babs = [b for b in bab_positions if start_chapter <= b['number'] <= end_chapter]
            
            if not filtered_babs:
                logger.warning(f"BAB {start_chapter}-{end_chapter} tidak ditemukan. Menggunakan full text.")
                return full_text
            
            # Ambil dari awal bab pertama sampai akhir bab terakhir
            start_pos = filtered_babs[0]['start']
            
            # Cari batas akhir: bab setelah end_chapter atau "DAFTAR PUSTAKA"
            end_pos = len(work_text)
            
            # Cari bab setelah end_chapter
            next_babs = [b for b in bab_positions if b['number'] > end_chapter]
            if next_babs:
                end_pos = next_babs[0]['start']
            
            # Atau cari "DAFTAR PUSTAKA"
            dafpus_match = re.search(r'(?i)^[\s]*DAFTAR\s+PUSTAKA\b', work_text[start_pos:], re.MULTILINE)
            if dafpus_match:
                dafpus_pos = start_pos + dafpus_match.start()
                if dafpus_pos < end_pos:
                    end_pos = dafpus_pos
            
            extracted = work_text[start_pos:end_pos].strip()
            
            logger.info(f"Extracted BAB {start_chapter}-{end_chapter}: {len(extracted)} chars (from {len(full_text)} total)")
            logger.info(f"Found chapters: {[b['number'] for b in filtered_babs]}")
            
            return extracted
            
        except Exception as e:
            logger.error(f"Error extracting chapters: {e}")
            return self.extract_text(pdf_path)  # Fallback ke full text
    
    def extract_abstract(self, pdf_path: str) -> Optional[str]:
        """
        Extract bagian abstrak dari PDF
        Mencari section yang dimulai dengan "Abstract" atau "ABSTRAK"
        
        Args:
            pdf_path: Path ke file PDF
            
        Returns:
            Text abstrak atau None
        """
        try:
            full_text = self.extract_text(pdf_path)
            
            # Pattern untuk mencari abstrak
            patterns = [
                r'(?i)abstract\s*[\:\-]?\s*(.*?)(?=\n\s*\n|\n[A-Z][a-z]+\s*[\:\-]|$)',
                r'(?i)abstrak\s*[\:\-]?\s*(.*?)(?=\n\s*\n|\n[A-Z][a-z]+\s*[\:\-]|$)',
                r'(?i)abstract\b(.*?)(?=\bintroduction\b|\bpendahuluan\b|\bkeywords\b|\bkata kunci\b)',
                r'(?i)abstrak\b(.*?)(?=\bintroduction\b|\bpendahuluan\b|\bkeywords\b|\bkata kunci\b)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, full_text, re.DOTALL)
                if match:
                    abstract = match.group(1).strip()
                    if len(abstract) > 50:  # Minimal 50 karakter
                        logger.info(f"Abstract found: {len(abstract)} characters")
                        return abstract
            
            logger.warning("Abstract section not found. Using first 500 words.")
            # Fallback: ambil 500 kata pertama
            words = full_text.split()[:500]
            return ' '.join(words)
            
        except Exception as e:
            logger.error(f"Error extracting abstract: {e}")
            return None
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, any]:
        """
        Get informasi metadata dari PDF
        
        Args:
            pdf_path: Path ke file PDF
            
        Returns:
            Dictionary berisi metadata PDF
        """
        try:
            info = {
                'num_pages': 0,
                'author': None,
                'title': None,
                'subject': None,
                'creator': None,
                'file_size': 0
            }
            
            # Get file size
            import os
            info['file_size'] = os.path.getsize(pdf_path)
            
            if self.use_pdfplumber:
                with pdfplumber.open(pdf_path) as pdf:
                    info['num_pages'] = len(pdf.pages)
                    if pdf.metadata:
                        info['author'] = pdf.metadata.get('Author')
                        info['title'] = pdf.metadata.get('Title')
                        info['subject'] = pdf.metadata.get('Subject')
                        info['creator'] = pdf.metadata.get('Creator')
            else:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    info['num_pages'] = len(pdf_reader.pages)
                    if pdf_reader.metadata:
                        info['author'] = pdf_reader.metadata.get('/Author')
                        info['title'] = pdf_reader.metadata.get('/Title')
                        info['subject'] = pdf_reader.metadata.get('/Subject')
                        info['creator'] = pdf_reader.metadata.get('/Creator')
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting PDF info: {e}")
            return info
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validasi apakah file adalah PDF yang valid
        
        Args:
            pdf_path: Path ke file PDF
            
        Returns:
            True jika valid, False jika tidak
        """
        try:
            with open(pdf_path, 'rb') as file:
                header = file.read(5)
                return header == b'%PDF-'
        except:
            return False
    
    def clean_extracted_text(self, text: str) -> str:
        """
        Membersihkan teks hasil ekstraksi dari karakter tidak diinginkan
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers (pattern: Page 1, Page 2, atau angka di awal baris)
        text = re.sub(r'(?m)^\s*\d+\s*$', '', text)
        text = re.sub(r'(?i)page\s+\d+', '', text)
        
        # Remove headers/footers yang berulang
        # (ini bisa disesuaikan dengan format dokumen spesifik)
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Strip whitespace
        text = text.strip()
        
        return text


# Testing
if __name__ == "__main__":
    processor = PDFProcessor(use_pdfplumber=True)
    
    # Test dengan sample PDF (ganti dengan path PDF yang sebenarnya)
    sample_pdf = "sample_abstrak.pdf"
    
    # Check if file exists
    import os
    if os.path.exists(sample_pdf):
        # Validate
        is_valid = processor.validate_pdf(sample_pdf)
        print(f"PDF Valid: {is_valid}")
        
        # Get info
        info = processor.get_pdf_info(sample_pdf)
        print(f"\nPDF Info:")
        print(f"Pages: {info['num_pages']}")
        print(f"Size: {info['file_size']} bytes")
        print(f"Title: {info['title']}")
        
        # Extract text
        text = processor.extract_text(sample_pdf)
        print(f"\nExtracted text ({len(text)} chars):")
        print(text[:200] + "...")
        
        # Extract abstract
        abstract = processor.extract_abstract(sample_pdf)
        if abstract:
            print(f"\nAbstract ({len(abstract)} chars):")
            print(abstract[:200] + "...")
    else:
        print(f"Sample PDF not found: {sample_pdf}")
        print("Create a sample PDF to test this module.")
