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


class PlagiarismDetector:
    """
    Kelas utama untuk deteksi plagiarisme semantik
    """
    
    def __init__(
        self,
        google_api_key: Optional[str] = None,
        google_cse_id: Optional[str] = None,
        model_name: str = "paraphrase-multilingual-mpnet-base-v2",
        similarity_threshold: float = 0.75,
        segment_size: int = 25,
        overlap: int = 5
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
        
        # Load Sentence-BERT model
        logger.info(f"Loading SBERT model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Setup Google CSE
        if self.google_api_key and self.google_cse_id:
            self.search_service = build("customsearch", "v1", developerKey=self.google_api_key)
        else:
            logger.warning("Google API credentials not provided. Search functionality disabled.")
            self.search_service = None
        
        logger.info("PlagiarismDetector initialized successfully")
    
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
            embedding1 = self.model.encode(text1, convert_to_tensor=True)
            embedding2 = self.model.encode(text2, convert_to_tensor=True)
            
            # Calculate cosine similarity
            similarity = util.cos_sim(embedding1, embedding2).item()
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def detect_segment_plagiarism(
        self,
        segment: Dict[str, any],
        search_results: List[Dict[str, str]]
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
        
        if not search_results:
            return {
                'segment_id': segment['segment_id'],
                'segment_text': segment_text,
                'word_count': segment['word_count'],
                'best_match': None,
                'similarity_score': 0.0,
                'label': 'Original',
                'source_url': None,
                'source_title': None,
                'all_matches': []
            }
        
        # Hitung similarity dengan semua snippets
        matches = []
        for result in search_results:
            snippet = result['snippet']
            similarity = self.calculate_similarity(segment_text, snippet)
            
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
    
    def detect_plagiarism(self, text: str, use_search: bool = True) -> Dict[str, any]:
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
            result = self.detect_segment_plagiarism(segment, search_results)
            detection_results.append(result)
            
            # Statistics
            if result['label'] == 'Plagiat':
                plagiarized_count += 1
            total_similarity += result['similarity_score']
        
        # Calculate overall statistics
        total_segments = len(segments)
        avg_similarity = total_similarity / total_segments if total_segments > 0 else 0.0
        plagiarism_percentage = (plagiarized_count / total_segments * 100) if total_segments > 0 else 0.0
        
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
