"""
Script untuk repair PDF yang rusak dan ekstrak teks
"""
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import sys

def repair_and_extract(pdf_path):
    """Coba repair PDF dan ekstrak teks"""
    print(f"Processing: {pdf_path}")
    
    try:
        # Coba baca dengan strict=False
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f, strict=False)
            print(f"Pages found: {len(reader.pages)}")
            
            # Coba ekstrak teks per halaman
            all_text = ""
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        print(f"Page {i+1}: {len(text)} characters")
                        all_text += text + "\n"
                    else:
                        print(f"Page {i+1}: No text (might be scanned image)")
                except Exception as e:
                    print(f"Page {i+1}: Error - {e}")
            
            if all_text.strip():
                print(f"\n✓ Total extracted: {len(all_text)} characters")
                print(f"\nFirst 500 chars:\n{all_text[:500]}")
                
                # Save to txt
                txt_path = pdf_path.replace('.pdf', '.txt')
                with open(txt_path, 'w', encoding='utf-8') as out:
                    out.write(all_text)
                print(f"\n✓ Saved to: {txt_path}")
                return all_text
            else:
                print("\n✗ No text extracted - PDF might be scanned images")
                print("  Solution: Use OCR tool or get the original Word/text document")
                return None
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    pdf_file = sys.argv[1] if len(sys.argv) > 1 else "skripsi_asli.pdf"
    repair_and_extract(pdf_file)
