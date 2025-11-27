# backend/extract_r67_to_txt.py
import PyPDF2

PDF_PATH = "R67.pdf"
TXT_PATH = "r67_full.txt"

def extract_pdf_to_txt(pdf_path: str, txt_path: str):
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        all_text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            all_text += page_text + "\n\n"

    # Optionnel : petit nettoyage
    all_text = all_text.replace("\u00ad", "")  # tirets de coupure
    all_text = all_text.replace("\r", "\n")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(all_text)

    print(f"Texte R67 extrait dans {txt_path}")

if __name__ == "__main__":
    extract_pdf_to_txt(PDF_PATH, TXT_PATH)