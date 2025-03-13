import fitz  # PyMuPDF
import os
import re
import json

# 📌 Define the output directory for the extracted text files
output_dir = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/extracted_index"
os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

# 📌 Load the list of PDFs and page ranges from vol.json
with open("/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/database/vol.json", "r", encoding="utf-8") as f:
    pdf_data = json.load(f)

# 📌 Function to correct common OCR errors
def correct_ocr_errors(text):
    """Fixes common OCR errors in the extracted text."""
    text = re.sub(r'(?<!\d)10(?!\d)', 'io', text)
    text = re.sub(r'(?<!\d)1(?!\d)', 'i', text)
    text = re.sub(r'\b1([a-záéíóúñü]+)\b', r'l\1', text)
    text = re.sub(r'(?<!\d)w(?!\d)', 'io', text)
    text = re.sub(r'\bm\b', 'in', text)
    text = re.sub(r'([A-ZÁÉÍÓÚÑÜ]{2,}),\s*([a-záéíóúñü])', lambda m: f"{m.group(1)}, {m.group(2).upper()}", text)
    text = re.sub(r'\b([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü]*)\b', lambda m: m.group(1).capitalize(), text)
    text = re.sub(r'\b(\w+)-\s+(\w+)\b', r'\1\2', text)
    text = re.sub(r'\s*-?\s*(\d{4,})\s*-?\s*', ' ', text)  # Remove apenas números longos (prováveis números de página)
    text = re.sub(r',\s*,+', ',', text)  # Remove múltiplas vírgulas
    text = text.strip(', ')  # Remove vírgulas e espaços extras
    return text

# 📌 Function to extract and clean text from PDFs
def extract_clean_text(pdf_path, start_page, end_page, volume):
    """Extracts and cleans text from a PDF within a given page range and saves it as a .txt file."""
    with fitz.open(pdf_path) as doc:
        full_text = ""
        for page_num in range(start_page - 1, end_page):  # Zero-based index
            full_text += doc[page_num].get_text("text") + "\n"
    
    # Apply OCR corrections
    cleaned_text = correct_ocr_errors(full_text)
    
    # Ensure numbers of letters are preserved
    cleaned_text = re.sub(r'(\d{1,3})(?=(\s*,\s*\d{1,3})+)', r'\1', cleaned_text)  # Mantém números de cartas
    cleaned_text = re.sub(r'(\d{1,3})$', r'\1', cleaned_text)  # Mantém números ao final da linha
    
    # Save to a .txt file
    output_path = os.path.join(output_dir, f"extracted_vol{volume}_index.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)
    
    print(f"✅ Cleaned text saved: {output_path}")

# 📌 Process all PDFs listed in vol.json
for item in pdf_data:
    extract_clean_text(item["pdf_path"], item["start_page"], item["end_page"], item["volume"])