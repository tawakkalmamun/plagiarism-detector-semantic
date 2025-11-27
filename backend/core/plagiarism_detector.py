"""
Core Plagiarism Detection Engine
Integrasi Google CSE dan Sentence-BERT untuk Deteksi Plagiarisme Semantik
"""

import os
import re
import numpy as np
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer, util
from googleapiclient.discovery import build
from loguru import logger
import torch
from functools import lru_cache



class PlagiarismDetector:
    """
    Kelas utama untuk deteksi plagiarisme semantik
    """
    
    def __init__(
        self,
        google_api_key: Optional[str] = None,
        google_cse_id: Optional[str] = None,
        model_name: str = "paraphrase-multilingual-mpnet-base-v2",
        fallback_model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.75,
        segment_size: int = 25,
        overlap: int = 5,
        cache_size: int = 512
    ):
        """
        Inisialisasi Plagiarism Detector
        
        Args:
            google_api_key: Google API Key untuk CSE
            google_cse_id: Google Custom Search Engine ID
            model_name: Nama model Sentence-BERT
            similarity_threshold: Threshold untuk klasifikasi plagiat (0-1)
            segment_size: Jumlah kata per segment
            overlap: Jumlah kata overlap antar segment
        """
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = google_cse_id or os.getenv("GOOGLE_CSE_ID")
        self.similarity_threshold = similarity_threshold
        self.segment_size = segment_size
        self.overlap = overlap
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.cache_size = cache_size

        # Load Sentence-BERT model dengan fallback & logging yang lebih informatif
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.model = self._load_model_with_fallback()

        # Simple embedding cache (LRU via decorator for text->embedding mapping)
        # Cache tingkat instance untuk segment embeddings agar tidak dihitung ulang saat similarity antar banyak snippet.
        self._segment_embedding_cache: Dict[str, torch.Tensor] = {}
        # Local corpus (list of dict: {source_id, text, embedding}) untuk pembanding non-Google
        self.local_corpus: List[Dict[str, any]] = []
        # Metadata untuk versi format penyimpanan
        self._corpus_format_version = 1
        
        # Setup Google CSE
        if self.google_api_key and self.google_cse_id:
            try:
                self.search_service = build("customsearch", "v1", developerKey=self.google_api_key)
            except Exception as e:
                logger.error(f"Gagal inisialisasi Google CSE: {e}")
                self.search_service = None
        else:
            logger.warning("Google API credentials not provided. Search functionality disabled.")
            self.search_service = None

        logger.info("PlagiarismDetector initialized successfully")

    def _load_model_with_fallback(self):
        """Memuat model utama dengan fallback ke model yang lebih ringan jika gagal."""
        try:
            logger.info(f"Memuat model SBERT utama: {self.model_name} (device={self.device})")
            model = SentenceTransformer(self.model_name, device=self.device)
            return model
        except Exception as e:
            logger.error(f"Gagal memuat model utama '{self.model_name}': {e}")
            logger.info(f"Mencoba fallback model: {self.fallback_model_name}")
            try:
                model = SentenceTransformer(self.fallback_model_name, device=self.device)
                logger.info("Fallback model berhasil dimuat")
                return model
            except Exception as e2:
                logger.error(f"Fallback model juga gagal dimuat: {e2}")
                raise RuntimeError("Tidak dapat memuat model SBERT apapun.")

    @lru_cache(maxsize=1024)
    def _encode_text_cached(self, text: str) -> torch.Tensor:
        """Encode teks dengan cache LRU (per proses)."""
        return self.model.encode(text, convert_to_tensor=True, device=self.device)

    def _get_segment_embedding(self, text: str) -> torch.Tensor:
        """Ambil embedding segment dari cache instance, jika penuh lakukan eviction sederhana."""
        if text in self._segment_embedding_cache:
            return self._segment_embedding_cache[text]
        emb = self._encode_text_cached(text)
        if len(self._segment_embedding_cache) >= self.cache_size:
            # Evict first inserted (simple FIFO); bisa ditingkatkan ke LRU penuh bila perlu
            self._segment_embedding_cache.pop(next(iter(self._segment_embedding_cache)))
        self._segment_embedding_cache[text] = emb
        return emb

    def add_to_corpus(self, text: str, source_id: str = "local") -> int:
        """Tambahkan teks penuh ke local corpus (di-segmentasi dan di-embed batch). Return jumlah segmen ditambahkan."""
        segments = self.segment_text(text)
        # Ambil list teks segmen
        segment_texts = [s['segment_text'] for s in segments]
        if not segment_texts:
            return 0
        try:
            embeddings = self.model.encode(segment_texts, convert_to_tensor=True, device=self.device)
        except Exception as e:
            logger.error(f"Gagal batch encode corpus: {e}")
            # Fallback per-segment
            embeddings = [self._get_segment_embedding(t) for t in segment_texts]
        # Simpan
        added = 0
        for seg, emb in zip(segments, embeddings):
            self.local_corpus.append({
                'source_id': source_id,
                'segment_id': seg['segment_id'],
                'text': seg['segment_text'],
                'embedding': emb
            })
            added += 1
        logger.info(f"Added {added} segments to local corpus (source_id={source_id}). Total corpus size: {len(self.local_corpus)}")
        return added

    def build_corpus_from_folder(self, folder_path: str, file_extension: str = ".pdf") -> Dict[str, any]:
        """
        Build corpus dari semua file dalam folder (biasanya PDF/TXT skripsi lama).
        
        Args:
            folder_path: Path ke folder berisi file corpus
            file_extension: Extension file yang diproses (.pdf atau .txt)
            
        Returns:
            Dictionary hasil build: jumlah file, jumlah segment, error list
        """
        logger.info(f"Building corpus from folder: {folder_path}")
        
        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return {
                'success': False,
                'message': f'Folder tidak ditemukan: {folder_path}',
                'files_processed': 0,
                'total_segments': 0,
                'errors': []
            }
        
        # Import pdf_processor_full di sini untuk menghindari circular import
        try:
            from .pdf_processor_full import PDFProcessor
            pdf_processor = PDFProcessor(use_pdfplumber=True)
        except ImportError:
            logger.warning("pdf_processor_full not available, using simplified version")
            from .pdf_processor import PDFProcessor
            pdf_processor = PDFProcessor()
        
        files_processed = 0
        total_segments = 0
        errors = []
        
        # Scan semua file di folder
        for filename in os.listdir(folder_path):
            if not filename.endswith(file_extension):
                continue
            
            file_path = os.path.join(folder_path, filename)
            source_id = f"corpus_{filename}"
            
            try:
                logger.info(f"Processing {filename}...")
                
                # Ekstrak teks
                if file_extension == ".pdf":
                    text = pdf_processor.extract_text(file_path)
                elif file_extension == ".txt":
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                else:
                    logger.warning(f"Unsupported file type: {filename}")
                    continue
                
                # Validasi teks
                if not text or len(text.strip()) < 100:
                    logger.warning(f"Text too short in {filename}, skipping")
                    errors.append(f"{filename}: Text too short")
                    continue
                
                # Tambahkan ke corpus
                segments_added = self.add_to_corpus(text, source_id=source_id)
                files_processed += 1
                total_segments += segments_added
                
                logger.info(f"✓ {filename}: {segments_added} segments added")
                
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
                errors.append(f"{filename}: {str(e)}")
        
        result = {
            'success': files_processed > 0,
            'message': f'Successfully processed {files_processed} files',
            'files_processed': files_processed,
            'total_segments': total_segments,
            'corpus_size': len(self.local_corpus),
            'errors': errors
        }
        
        logger.info(f"Corpus build completed: {files_processed} files, {total_segments} segments, {len(errors)} errors")
        return result

    def clear_corpus(self):
        """Clear semua corpus lokal."""
        count = len(self.local_corpus)
        self.local_corpus = []
        logger.info(f"Cleared {count} segments from local corpus")
        return count

    def save_corpus(self, path: str) -> Dict[str, any]:
        """Simpan corpus lokal (teks + embeddings) ke file pickle.

        Embedding disimpan sebagai list float agar portable.
        """
        import pickle, time
        os.makedirs(os.path.dirname(path), exist_ok=True)
        start = time.time()
        serializable = {
            'format_version': self._corpus_format_version,
            'model_name': self.model_name,
            'segments': [
                {
                    'source_id': item['source_id'],
                    'segment_id': item['segment_id'],
                    'text': item['text'],
                    'embedding': item['embedding'].detach().cpu().tolist()
                }
                for item in self.local_corpus
            ]
        }
        with open(path, 'wb') as f:
            pickle.dump(serializable, f, protocol=pickle.HIGHEST_PROTOCOL)
        dur = round(time.time() - start, 2)
        logger.info(f"Saved corpus ({len(self.local_corpus)} segments) to {path} in {dur}s")
        return {'success': True, 'segments': len(self.local_corpus), 'path': path, 'time_sec': dur}

    def load_corpus(self, path: str) -> Dict[str, any]:
        """Muat corpus lokal dari file pickle."""
        import pickle, time
        if not os.path.exists(path):
            logger.warning(f"Corpus file not found: {path}")
            return {'success': False, 'segments': 0, 'path': path, 'message': 'File not found'}
        start = time.time()
        with open(path, 'rb') as f:
            data = pickle.load(f)
        fmt = data.get('format_version', 0)
        segments_raw = data.get('segments', [])
        reconstructed = []
        for seg in segments_raw:
            emb_list = seg.get('embedding', [])
            try:
                emb_tensor = torch.tensor(emb_list, device=self.device)
            except Exception:
                emb_tensor = self._encode_text_cached(seg['text'])
            reconstructed.append({
                'source_id': seg['source_id'],
                'segment_id': seg['segment_id'],
                'text': seg['text'],
                'embedding': emb_tensor
            })
        self.local_corpus = reconstructed
        dur = round(time.time() - start, 2)
        logger.info(f"Loaded corpus ({len(self.local_corpus)} segments) from {path} in {dur}s (format v{fmt})")
        return {'success': True, 'segments': len(self.local_corpus), 'path': path, 'format_version': fmt, 'time_sec': dur}

    def get_corpus_info(self) -> Dict[str, any]:
        """Get informasi tentang corpus saat ini."""
        if not self.local_corpus:
            return {
                'size': 0,
                'sources': [],
                'empty': True
            }
        
        # Hitung source yang unik
        sources = {}
        for item in self.local_corpus:
            source_id = item['source_id']
            sources[source_id] = sources.get(source_id, 0) + 1
        
        return {
            'size': len(self.local_corpus),
            'sources': [{'source_id': k, 'segments': v} for k, v in sources.items()],
            'empty': False
        }

    def _match_local_corpus(self, segment_text: str, segment_embedding: torch.Tensor) -> Optional[Dict[str, any]]:
        """Cari best match di local corpus menggunakan cosine similarity batch."""
        if not self.local_corpus:
            return None
        try:
            corpus_embeddings = torch.stack([item['embedding'] for item in self.local_corpus])
            # Expand segment embedding
            scores = util.cos_sim(segment_embedding, corpus_embeddings)[0]  # shape (N,)
            best_idx = int(torch.argmax(scores).item())
            best_score = float(scores[best_idx].item())
            best_item = self.local_corpus[best_idx]
            return {
                'snippet': best_item['text'],
                'similarity': best_score,
                'url': None,
                'title': f"LOCAL:{best_item['source_id']}",
                'source': 'local_corpus'
            }
        except Exception as e:
            logger.error(f"Gagal match local corpus: {e}")
            return None
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocessing teks: cleaning dan normalisasi
        
        Args:
            text: Teks input
            
        Returns:
            Teks yang sudah dibersihkan
        """
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters (keep punctuation)
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text)
        
        # Strip
        text = text.strip()
        
        return text
    
    def segment_text(self, text: str) -> List[Dict[str, any]]:
        """
        Memotong teks menjadi segmen-segmen menggunakan sliding window
        
        Args:
            text: Teks yang akan dipotong
            
        Returns:
            List of segments dengan metadata
        """
        # Preprocessing
        text = self.preprocess_text(text)
        
        # Split into words
        words = text.split()
        
        segments = []
        segment_id = 1
        i = 0
        
        while i < len(words):
            # Ambil segment_size kata
            segment_words = words[i:i + self.segment_size]
            segment_text = ' '.join(segment_words)
            
            segments.append({
                'segment_id': segment_id,
                'segment_text': segment_text,
                'start_word': i,
                'end_word': i + len(segment_words),
                'word_count': len(segment_words)
            })
            
            segment_id += 1
            
            # Slide window dengan overlap
            i += (self.segment_size - self.overlap)
            
            # Break jika sisa kata kurang dari minimum
            if len(words) - i < 10:  # Minimum 10 kata untuk segment terakhir
                if i < len(words):
                    # Tambahkan sisa kata sebagai segment terakhir
                    last_segment_words = words[i:]
                    last_segment_text = ' '.join(last_segment_words)
                    segments.append({
                        'segment_id': segment_id,
                        'segment_text': last_segment_text,
                        'start_word': i,
                        'end_word': len(words),
                        'word_count': len(last_segment_words)
                    })
                break
        
        logger.info(f"Text segmented into {len(segments)} segments")
        return segments
    
    def search_google(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Mencari referensi di Google menggunakan Custom Search Engine
        
        Args:
            query: Query pencarian
            num_results: Jumlah hasil yang diinginkan
            
        Returns:
            List of search results dengan snippet dan URL
        """
        if not self.search_service:
            logger.warning("Google Search service not available")
            return []
        
        try:
            # Batasi panjang query (max 128 chars untuk CSE)
            query = query[:128]
            
            # Execute search
            result = self.search_service.cse().list(
                q=query,
                cx=self.google_cse_id,
                num=num_results
            ).execute()
            
            # Extract snippets and URLs
            search_results = []
            if 'items' in result:
                for item in result['items']:
                    search_results.append({
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'url': item.get('link', ''),
                        'source': item.get('displayLink', '')
                    })
            
            logger.info(f"Found {len(search_results)} results for query: {query[:50]}...")
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching Google: {e}")
            return []
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Menghitung semantic similarity antara dua teks menggunakan SBERT
        
        Args:
            text1: Teks pertama
            text2: Teks kedua
            
        Returns:
            Similarity score (0-1)
        """
        try:
            # Encode texts
            embedding1 = self._get_segment_embedding(text1)
            embedding2 = self._encode_text_cached(text2)
            
            # Calculate cosine similarity
            similarity = util.cos_sim(embedding1, embedding2).item()
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def detect_segment_plagiarism(
        self,
        segment: Dict[str, any],
        search_results: List[Dict[str, str]],
        precomputed_embedding: Optional[torch.Tensor] = None,
        use_local_corpus: bool = True
    ) -> Dict[str, any]:
        """
        Mendeteksi plagiarisme untuk satu segment
        
        Args:
            segment: Dictionary segment teks
            search_results: List hasil pencarian Google
            
        Returns:
            Dictionary hasil deteksi untuk segment
        """
        segment_text = segment['segment_text']
        
        # Precomputed embedding (batch) atau ambil dari cache
        segment_embedding = precomputed_embedding if precomputed_embedding is not None else self._get_segment_embedding(segment_text)

        # Jika tidak ada hasil pencarian Google, coba local corpus
        if not search_results:
            local_match = self._match_local_corpus(segment_text, segment_embedding) if use_local_corpus else None
            similarity_score = local_match['similarity'] if local_match else 0.0
            label = 'Plagiat' if local_match and similarity_score >= self.similarity_threshold else 'Original'
            return {
                'segment_id': segment['segment_id'],
                'segment_text': segment_text,
                'word_count': segment['word_count'],
                'best_match': local_match['snippet'] if local_match else None,
                'similarity_score': similarity_score,
                'label': label,
                'source_url': None,
                'source_title': local_match['title'] if local_match else None,
                'source_domain': local_match['source'] if local_match else None,
                'all_matches': [local_match] if local_match else []
            }
        
        # Hitung similarity dengan semua snippets
        # segment_embedding sudah disiapkan
        matches = []
        for result in search_results:
            snippet = result['snippet']
            try:
                snippet_embedding = self._encode_text_cached(snippet)
                similarity = util.cos_sim(segment_embedding, snippet_embedding).item()
            except Exception as e:
                logger.error(f"Gagal hitung similarity snippet: {e}")
                similarity = 0.0
            matches.append({
                'snippet': snippet,
                'similarity': similarity,
                'url': result['url'],
                'title': result['title'],
                'source': result['source']
            })
        
        # Sort by similarity (descending)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Ambil best match
        best_match = matches[0] if matches else None
        
        # Klasifikasi
        if best_match and best_match['similarity'] >= self.similarity_threshold:
            label = 'Plagiat'
        else:
            label = 'Original'
        
        return {
            'segment_id': segment['segment_id'],
            'segment_text': segment_text,
            'word_count': segment['word_count'],
            'best_match': best_match['snippet'] if best_match else None,
            'similarity_score': best_match['similarity'] if best_match else 0.0,
            'label': label,
            'source_url': best_match['url'] if best_match else None,
            'source_title': best_match['title'] if best_match else None,
            'source_domain': best_match['source'] if best_match else None,
            'all_matches': matches[:3]  # Top 3 matches
        }
    
    def detect_plagiarism(self, text: str, use_search: bool = True, use_local_corpus: bool = True, add_to_corpus: bool = False, corpus_source_id: Optional[str] = None) -> Dict[str, any]:
        """
        Deteksi plagiarisme untuk seluruh teks
        
        Args:
            text: Teks yang akan dianalisis
            use_search: Apakah menggunakan Google search
            
        Returns:
            Dictionary hasil deteksi lengkap
        """
        logger.info("Starting plagiarism detection...")
        
        # Segmentasi teks
        segments = self.segment_text(text)
        
        # Batch embedding untuk semua segmen (optimasi)
        segment_texts = [s['segment_text'] for s in segments]
        try:
            batch_embeddings = self.model.encode(segment_texts, convert_to_tensor=True, device=self.device)
        except Exception as e:
            logger.error(f"Gagal batch encode segmen: {e}. Fallback per-segment.")
            batch_embeddings = [self._get_segment_embedding(t) for t in segment_texts]

        # Deteksi per segment
        detection_results = []
        plagiarized_count = 0
        total_similarity = 0.0
        
        for idx, segment in enumerate(segments, 1):
            logger.info(f"Processing segment {idx}/{len(segments)}")
            
            # Search Google jika enabled
            if use_search and self.search_service:
                search_results = self.search_google(segment['segment_text'])
            else:
                search_results = []
            
            # Detect plagiarism
            # Ambil embedding batch
            embedding = batch_embeddings[idx-1] if isinstance(batch_embeddings, torch.Tensor) else batch_embeddings[idx-1]
            result = self.detect_segment_plagiarism(segment, search_results, precomputed_embedding=embedding, use_local_corpus=use_local_corpus)
            detection_results.append(result)
            
            # Statistics
            if result['label'] == 'Plagiat':
                plagiarized_count += 1
            total_similarity += result['similarity_score']
        
        # Calculate overall statistics
        total_segments = len(segments)
        avg_similarity = total_similarity / total_segments if total_segments > 0 else 0.0
        plagiarism_percentage = (plagiarized_count / total_segments * 100) if total_segments > 0 else 0.0
        
        # Tambah ke corpus jika diminta
        if add_to_corpus:
            source_id = corpus_source_id or "task_corpus"
            try:
                self.add_to_corpus(text, source_id=source_id)
            except Exception as e:
                logger.error(f"Gagal menambah ke corpus: {e}")

        final_result = {
            'total_segments': total_segments,
            'plagiarized_segments': plagiarized_count,
            'original_segments': total_segments - plagiarized_count,
            'plagiarism_percentage': round(plagiarism_percentage, 2),
            'avg_similarity': round(avg_similarity, 4),
            'threshold_used': self.similarity_threshold,
            'details': detection_results
        }
        
        logger.info(f"Detection completed. Plagiarism: {plagiarism_percentage:.2f}%")
        return final_result


# Helper function untuk testing
if __name__ == "__main__":
    # Sample text untuk testing
    sample_text = """
    Penelitian ini bertujuan untuk mengembangkan sistem deteksi plagiarisme 
    berbasis semantik menggunakan integrasi Google Custom Search Engine dan 
    Sentence-BERT. Metode yang digunakan adalah sliding window untuk segmentasi 
    teks dan cosine similarity untuk pengukuran kemiripan. Hasil penelitian 
    menunjukkan bahwa sistem mampu mendeteksi parafrase dengan akurasi tinggi.
    """
    
    # Initialize detector
    detector = PlagiarismDetector(
        similarity_threshold=0.75,
        segment_size=25,
        overlap=5
    )
    
    # Test segmentation
    segments = detector.segment_text(sample_text)
    print(f"\nTotal segments: {len(segments)}")
    for seg in segments:
        print(f"Segment {seg['segment_id']}: {seg['segment_text'][:50]}...")
    
    # Test similarity
    text1 = "Penelitian ini bertujuan untuk mengembangkan sistem"
    text2 = "This research aims to develop a system"
    similarity = detector.calculate_similarity(text1, text2)
    print(f"\nSimilarity: {similarity:.4f}")
