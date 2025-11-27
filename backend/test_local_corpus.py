import pytest
from core.plagiarism_detector import PlagiarismDetector


def test_local_corpus_similarity():
    """Memastikan local corpus dapat mendeteksi kemiripan semantik antar dua teks mirip."""
    pd = PlagiarismDetector(similarity_threshold=0.6, segment_size=20, overlap=5)

    text1 = (
        "Machine learning adalah cabang dari kecerdasan buatan yang mempelajari pola dari data. "
        "Model pembelajaran mendalam seperti transformer mampu memahami konteks kalimat. "
        "Teknik embedding membuat representasi vektor semantik untuk setiap segmen."
    )
    text2 = (
        "Machine learning merupakan bagian dari AI yang mempelajari pola data. "
        "Representasi vektor semantik dihasilkan melalui teknik embedding sehingga model transformer dapat menangkap konteks kalimat secara mendalam."
    )

    # Tambahkan teks pertama ke corpus lokal
    added = pd.add_to_corpus(text1, source_id="t1")
    assert added > 0, "Segment corpus tidak bertambah"

    # Deteksi teks kedua menggunakan local corpus tanpa Google search
    result = pd.detect_plagiarism(text2, use_search=False, use_local_corpus=True, add_to_corpus=False)

    # Harus ada segmen terdeteksi sebagai plagiat (label asli mesin 'Plagiat')
    assert result['plagiarized_segments'] > 0, "Tidak ada segmen plagiat terdeteksi padahal teks mirip"
    assert any(d['label'] == 'Plagiat' for d in result['details']), "Label 'Plagiat' tidak muncul"
    assert result['plagiarism_percentage'] > 0.0, "Persentase plagiarisme harus > 0"

    # Cek rata-rata similarity wajar (>= threshold * 0.5 sebagai sanity check)
    assert result['avg_similarity'] >= 0.3, f"Similarity rata-rata terlalu rendah: {result['avg_similarity']}"
