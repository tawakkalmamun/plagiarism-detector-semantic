"""
Sample Data untuk Testing Sistem Deteksi Plagiarisme
"""

# Sample abstracts untuk testing (dalam Bahasa Indonesia)

SAMPLE_ABSTRACT_1 = """
ABSTRAK

Penelitian ini bertujuan untuk mengembangkan sistem deteksi plagiarisme berbasis 
semantik yang mampu mendeteksi kemiripan makna pada abstrak skripsi mahasiswa. 
Metode yang digunakan adalah integrasi Google Custom Search Engine untuk pencarian 
referensi dari internet dan Sentence-BERT untuk analisis kemiripan semantik. 
Sistem menggunakan teknik sliding window dengan ukuran 25 kata per segmen dan 
overlap 5 kata untuk memotong teks. Setiap segmen dicari referensinya di Google, 
kemudian dihitung kemiripan semantiknya menggunakan cosine similarity. Hasil 
penelitian menunjukkan bahwa sistem mampu mendeteksi plagiarisme semantik dengan 
akurasi tinggi, bahkan pada teks yang sudah diparafrase. Sistem ini diharapkan 
dapat membantu pihak akademik dalam melakukan verifikasi keaslian karya ilmiah 
mahasiswa.

Kata Kunci: plagiarisme semantik, sentence-bert, google cse, deteksi parafrase
"""

SAMPLE_ABSTRACT_2 = """
ABSTRAK

Machine learning merupakan cabang dari artificial intelligence yang fokus pada 
pengembangan algoritma yang dapat belajar dari data. Dalam penelitian ini, 
digunakan metode deep learning untuk klasifikasi citra medis. Dataset yang 
digunakan terdiri dari 10.000 gambar X-ray dengan 5 kategori penyakit. Model 
yang dikembangkan menggunakan arsitektur Convolutional Neural Network (CNN) 
dengan transfer learning dari ResNet-50. Hasil eksperimen menunjukkan akurasi 
95% pada data testing. Sistem ini dapat membantu dokter dalam melakukan diagnosis 
awal penyakit berdasarkan citra medis. Implementasi dilakukan menggunakan 
framework TensorFlow dan Keras dengan bahasa pemrograman Python.

Kata Kunci: machine learning, deep learning, CNN, klasifikasi citra, diagnosis medis
"""

SAMPLE_ABSTRACT_3 = """
ABSTRAK

Internet of Things (IoT) adalah konsep dimana objek fisik dapat terhubung ke 
internet dan saling berkomunikasi. Penelitian ini mengembangkan sistem monitoring 
suhu dan kelembaban berbasis IoT untuk greenhouse pertanian. Hardware yang 
digunakan adalah mikrokontroler ESP32, sensor DHT22, dan relay untuk kontrol 
otomatis. Data sensor dikirim ke cloud platform ThingSpeak melalui protokol MQTT. 
Dashboard web dikembangkan untuk visualisasi data real-time dan analisis historis. 
Sistem dilengkapi dengan notifikasi otomatis via Telegram jika parameter melewati 
threshold. Hasil pengujian menunjukkan sistem dapat bekerja stabil selama 24/7 
dengan akurasi pengukuran suhu ±0.5°C dan kelembaban ±2%. Sistem ini dapat 
meningkatkan efisiensi pertanian dengan monitoring dan kontrol otomatis.

Kata Kunci: Internet of Things, monitoring, ESP32, greenhouse, pertanian pintar
"""

# Sample text yang sudah diparafrase (untuk testing deteksi parafrase)
PARAPHRASED_TEXT = """
Riset ini memiliki tujuan untuk membangun sebuah sistem pendeteksi plagiat yang 
berbasis pada kemiripan makna, yang bisa mengidentifikasi kesamaan arti dalam 
ringkasan tugas akhir mahasiswa. Pendekatan yang diterapkan adalah penggabungan 
Google Custom Search Engine untuk mencari rujukan dari dunia maya dan Sentence-BERT 
untuk menganalisis kemiripan dari segi semantik. Sistem memanfaatkan metode 
sliding window dengan besaran 25 kata tiap segmen serta overlap 5 kata untuk 
memecah teks. Tiap-tiap segmen dicarikan referensinya melalui Google, lalu 
dikalkulasi kemiripan semantiknya dengan menggunakan cosine similarity.
"""

# Test cases untuk unit testing
TEST_CASES = [
    {
        "id": "TC001",
        "text": "Penelitian ini bertujuan untuk mengembangkan sistem",
        "expected_segments": 1,
        "description": "Short text - single segment"
    },
    {
        "id": "TC002",
        "text": SAMPLE_ABSTRACT_1,
        "expected_segments": 7,
        "description": "Full abstract - multiple segments"
    },
    {
        "id": "TC003",
        "text": "A" * 10000,  # Very long text
        "expected_segments": 200,
        "description": "Very long text - many segments"
    },
    {
        "id": "TC004",
        "text": "   Multiple    spaces    between    words   ",
        "expected_segments": 1,
        "description": "Text with irregular spacing"
    }
]

# Sample similarity scores untuk testing classifier
SAMPLE_SIMILARITIES = [
    {"score": 0.95, "expected_label": "Plagiat"},
    {"score": 0.85, "expected_label": "Plagiat"},
    {"score": 0.76, "expected_label": "Plagiat"},
    {"score": 0.74, "expected_label": "Original"},
    {"score": 0.50, "expected_label": "Original"},
    {"score": 0.30, "expected_label": "Original"},
]

# Sample Google CSE responses (untuk testing tanpa API call)
MOCK_SEARCH_RESULTS = [
    {
        "title": "Semantic Plagiarism Detection Using BERT",
        "snippet": "This research aims to develop a semantic-based plagiarism detection system capable of detecting similarity in meaning in student thesis abstracts.",
        "url": "https://example.com/paper1",
        "source": "example.com"
    },
    {
        "title": "Machine Learning for Text Similarity",
        "snippet": "The method used is the integration of search engines for reference search from the internet and Sentence-BERT for semantic similarity analysis.",
        "url": "https://example.com/paper2",
        "source": "example.com"
    },
    {
        "title": "Paraphrase Detection in Academic Writing",
        "snippet": "The system uses a sliding window technique with a size of 25 words per segment and an overlap of 5 words to cut the text.",
        "url": "https://example.com/paper3",
        "source": "example.com"
    }
]

if __name__ == "__main__":
    print("Sample Data for Plagiarism Detection System")
    print("=" * 50)
    print(f"\nSample Abstract 1 Length: {len(SAMPLE_ABSTRACT_1)} characters")
    print(f"Sample Abstract 2 Length: {len(SAMPLE_ABSTRACT_2)} characters")
    print(f"Sample Abstract 3 Length: {len(SAMPLE_ABSTRACT_3)} characters")
    print(f"\nTotal Test Cases: {len(TEST_CASES)}")
    print(f"Mock Search Results: {len(MOCK_SEARCH_RESULTS)}")
