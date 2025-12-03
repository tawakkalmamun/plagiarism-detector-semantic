"""
Script helper untuk build local corpus dari folder PDF/TXT skripsi lama.

Usage:
    python build_corpus.py --folder uploads/corpus_skripsi --extension .pdf
    python build_corpus.py --folder data/corpus_txt --extension .txt --clear
"""

import argparse
import sys
import os
from loguru import logger

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.plagiarism_detector import PlagiarismDetector


def main():
    parser = argparse.ArgumentParser(description='Build local corpus dari folder skripsi')
    parser.add_argument(
        '--folder', 
        type=str, 
        default='uploads/corpus_skripsi',
        help='Path ke folder berisi file corpus (default: uploads/corpus_skripsi)'
    )
    parser.add_argument(
        '--extension',
        type=str,
        default='.pdf',
        choices=['.pdf', '.txt'],
        help='Extension file yang akan diproses (default: .pdf)'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Hapus corpus yang ada sebelum build baru'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.75,
        help='Similarity threshold untuk deteksi (default: 0.75)'
    )
    
    args = parser.parse_args()
    
    # Banner
    print("\n" + "="*60)
    print("🔍 PLAGIARISM DETECTOR - LOCAL CORPUS BUILDER")
    print("="*60 + "\n")
    
    # Initialize detector
    print("📦 Initializing Plagiarism Detector...")
    detector = PlagiarismDetector(
        similarity_threshold=args.threshold,
        segment_size=25,
        overlap=5
    )
    
    # Clear existing corpus jika diminta
    if args.clear:
        print("\n🗑️  Clearing existing corpus...")
        cleared = detector.clear_corpus()
        print(f"   Cleared {cleared} segments")
    
    # Check folder
    if not os.path.exists(args.folder):
        print(f"\n❌ Error: Folder tidak ditemukan: {args.folder}")
        print(f"\n💡 Tip: Buat folder terlebih dahulu dan masukkan file {args.extension}")
        print(f"   mkdir -p {args.folder}")
        return 1
    
    # Count files
    files = [f for f in os.listdir(args.folder) if f.endswith(args.extension)]
    if not files:
        print(f"\n⚠️  Warning: Tidak ada file {args.extension} di folder {args.folder}")
        print(f"\n💡 Tip: Masukkan file skripsi (PDF/TXT) ke folder tersebut")
        return 1
    
    print(f"\n📂 Folder: {args.folder}")
    print(f"📄 Files found: {len(files)} file(s) dengan extension {args.extension}")
    print(f"\n⏳ Building corpus... (ini mungkin memakan waktu beberapa menit)\n")
    
    # Build corpus
    result = detector.build_corpus_from_folder(args.folder, args.extension)
    
    # Display results
    print("\n" + "="*60)
    print("📊 HASIL BUILD CORPUS")
    print("="*60)
    print(f"✅ Success: {result['success']}")
    print(f"📁 Files processed: {result['files_processed']}/{len(files)}")
    print(f"📝 Total segments: {result['total_segments']}")
    print(f"💾 Corpus size: {result['corpus_size']}")
    
    if result['errors']:
        print(f"\n⚠️  Errors ({len(result['errors'])}):")
        for error in result['errors'][:5]:  # Show max 5 errors
            print(f"   - {error}")
        if len(result['errors']) > 5:
            print(f"   ... and {len(result['errors']) - 5} more errors")
    
    # Get corpus info
    info = detector.get_corpus_info()
    print(f"\n📊 Corpus Info:")
    print(f"   Size: {info['size']} segments")
    print(f"   Sources: {len(info['sources'])} file(s)")
    if info['sources'][:3]:  # Show top 3 sources
        print(f"\n   Top sources:")
        for src in info['sources'][:3]:
            print(f"   - {src['source_id']}: {src['segments']} segments")
    
    # Save corpus to disk
    if result['success'] and result['corpus_size'] > 0:
        print(f"\n💾 Saving corpus to disk...")
        save_result = detector.save_corpus('data/corpus.pkl')
        if save_result['success']:
            print(f"   ✅ Saved {save_result['segments']} segments to {save_result['path']}")
        else:
            print(f"   ⚠️  Warning: Could not save corpus to disk")
    
    print("\n" + "="*60)
    if result['success']:
        print("✅ Corpus berhasil dibangun!")
        print("\n💡 Next steps:")
        print("   1. Jalankan server: python main.py")
        print("   2. Upload skripsi baru untuk deteksi")
        print("   3. Pastikan use_local_corpus=True saat deteksi")
    else:
        print("❌ Corpus build gagal atau tidak ada file yang berhasil diproses")
        print("\n💡 Troubleshooting:")
        print("   - Pastikan file PDF/TXT valid dan readable")
        print("   - Check logs di atas untuk detail error")
    print("="*60 + "\n")
    
    return 0 if result['success'] else 1


if __name__ == "__main__":
    sys.exit(main())
