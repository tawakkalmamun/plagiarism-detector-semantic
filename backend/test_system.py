"""
Testing Script untuk Sistem Deteksi Plagiarisme
Menguji berbagai komponen sistem
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.plagiarism_detector import PlagiarismDetector
from data.sample_data import (
    SAMPLE_ABSTRACT_1,
    SAMPLE_ABSTRACT_2,
    PARAPHRASED_TEXT,
    TEST_CASES,
    SAMPLE_SIMILARITIES
)


def test_text_segmentation():
    """Test text segmentation dengan sliding window"""
    print("\n" + "=" * 60)
    print("TEST 1: Text Segmentation")
    print("=" * 60)
    
    detector = PlagiarismDetector(segment_size=25, overlap=5)
    
    for test_case in TEST_CASES[:2]:  # Test first 2 cases
        print(f"\n{test_case['id']}: {test_case['description']}")
        print(f"Text length: {len(test_case['text'])} characters")
        
        segments = detector.segment_text(test_case['text'])
        
        print(f"Generated segments: {len(segments)}")
        print(f"Expected segments: {test_case['expected_segments']}")
        
        if len(segments) > 0:
            print(f"\nFirst segment:")
            print(f"  ID: {segments[0]['segment_id']}")
            print(f"  Text: {segments[0]['segment_text'][:100]}...")
            print(f"  Word count: {segments[0]['word_count']}")
        
        # Check if segments are within expected range (±20% tolerance)
        tolerance = test_case['expected_segments'] * 0.2
        if abs(len(segments) - test_case['expected_segments']) <= tolerance:
            print("✅ PASS")
        else:
            print("❌ FAIL")


def test_similarity_calculation():
    """Test similarity calculation menggunakan SBERT"""
    print("\n" + "=" * 60)
    print("TEST 2: Similarity Calculation")
    print("=" * 60)
    
    detector = PlagiarismDetector()
    
    test_pairs = [
        {
            "text1": "Penelitian ini bertujuan untuk mengembangkan sistem",
            "text2": "This research aims to develop a system",
            "expected": "HIGH (translation)"
        },
        {
            "text1": "Machine learning adalah cabang dari artificial intelligence",
            "text2": "Machine learning is a branch of artificial intelligence",
            "expected": "HIGH (translation)"
        },
        {
            "text1": "Sistem menggunakan teknologi IoT untuk monitoring",
            "text2": "Sistem deteksi plagiarisme menggunakan SBERT",
            "expected": "MEDIUM (related topic)"
        },
        {
            "text1": "Penelitian tentang deep learning untuk klasifikasi citra",
            "text2": "Analisis sentimen menggunakan natural language processing",
            "expected": "LOW (different topic)"
        }
    ]
    
    for i, pair in enumerate(test_pairs, 1):
        print(f"\nTest Pair {i}: {pair['expected']}")
        print(f"Text 1: {pair['text1']}")
        print(f"Text 2: {pair['text2']}")
        
        similarity = detector.calculate_similarity(pair['text1'], pair['text2'])
        print(f"Similarity Score: {similarity:.4f} ({similarity*100:.2f}%)")
        
        # Determine level
        if similarity >= 0.8:
            level = "HIGH"
        elif similarity >= 0.6:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        print(f"Detected Level: {level}")


def test_classification():
    """Test classification logic (plagiat vs original)"""
    print("\n" + "=" * 60)
    print("TEST 3: Classification Logic")
    print("=" * 60)
    
    detector = PlagiarismDetector(similarity_threshold=0.75)
    
    print(f"Threshold: {detector.similarity_threshold}")
    print("\nClassification results:")
    print("-" * 40)
    
    for sample in SAMPLE_SIMILARITIES:
        score = sample['score']
        expected = sample['expected_label']
        
        # Classify
        if score >= detector.similarity_threshold:
            detected = "Plagiat"
        else:
            detected = "Original"
        
        status = "✅" if detected == expected else "❌"
        print(f"{status} Score: {score:.2f} -> Detected: {detected:10s} (Expected: {expected})")


def test_full_detection():
    """Test full detection pipeline (tanpa Google search)"""
    print("\n" + "=" * 60)
    print("TEST 4: Full Detection Pipeline (Without Search)")
    print("=" * 60)
    
    detector = PlagiarismDetector(
        similarity_threshold=0.75,
        segment_size=25,
        overlap=5
    )
    
    print(f"\nTesting with Sample Abstract 1")
    print(f"Text length: {len(SAMPLE_ABSTRACT_1)} characters")
    
    # Detect without search (will have all Original since no references)
    result = detector.detect_plagiarism(SAMPLE_ABSTRACT_1, use_search=False)
    
    print(f"\nResults:")
    print(f"  Total Segments: {result['total_segments']}")
    print(f"  Plagiarized: {result['plagiarized_segments']}")
    print(f"  Original: {result['original_segments']}")
    print(f"  Plagiarism %: {result['plagiarism_percentage']:.2f}%")
    print(f"  Avg Similarity: {result['avg_similarity']:.4f}")
    
    # Show first few segments
    print(f"\nFirst 3 segments:")
    for detail in result['details'][:3]:
        print(f"  - Segment {detail['segment_id']}: {detail['segment_text'][:60]}...")
        print(f"    Score: {detail['similarity_score']:.4f}, Label: {detail['label']}")


def test_preprocessing():
    """Test text preprocessing"""
    print("\n" + "=" * 60)
    print("TEST 5: Text Preprocessing")
    print("=" * 60)
    
    detector = PlagiarismDetector()
    
    test_texts = [
        "   Multiple    spaces    between    words   ",
        "Text\nwith\nnewlines\neverywhere",
        "Text!!!with???special@@@characters###",
        "UPPERCASE text MIXED with lowercase"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}:")
        print(f"  Original: {repr(text)}")
        cleaned = detector.preprocess_text(text)
        print(f"  Cleaned:  {repr(cleaned)}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PLAGIARISM DETECTION SYSTEM - TESTING")
    print("=" * 60)
    
    try:
        test_text_segmentation()
        test_similarity_calculation()
        test_classification()
        test_preprocessing()
        test_full_detection()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   SISTEM DETEKSI PLAGIARISME SEMANTIK - TESTING       ║
    ║   Integrasi Google CSE dan Sentence-BERT              ║
    ║   UNISMUH Makassar                                     ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    run_all_tests()
    
    print("\n📝 Note: Testing dengan Google Search memerlukan API credentials")
    print("   Untuk testing lengkap, set GOOGLE_API_KEY dan GOOGLE_CSE_ID di .env")
