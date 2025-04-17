import pdfplumber
import os

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def save_text_to_file(text, output_path):
    """Save extracted text to a file."""
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text)
    print(f"Text extracted and saved to: {output_path}")

if __name__ == "__main__":
    # Define the base path
    base_path = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters"
    
    pdf_path = os.path.join(base_path, "01_Volume_I_colBN_C3_1_0_OCR.pdf")
    output_path = os.path.join(base_path, "extracted_text.txt")
    
    extracted_text = extract_text_from_pdf(pdf_path)
    save_text_to_file(extracted_text, output_path)
