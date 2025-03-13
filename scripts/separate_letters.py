import re
import os
from lingua import Language, LanguageDetectorBuilder

# Configure Lingua for language detection
detector = LanguageDetectorBuilder.from_languages(
    Language.SPANISH, Language.ITALIAN, Language.FRENCH, Language.PORTUGUESE, Language.ENGLISH
).build()

def detect_language(text):
    """Detect the language of the given text using Lingua."""
    try:
        language = detector.detect_language_of(text)
        return language.name.lower() if language else "unknown"
    except:
        return "unknown"

def split_letters(text):
    """
    Split the extracted text into individual letters.
    Ensures that dates or numbers in the text are not mistaken for delimiters.
    """
    # Match only numbers at the start of a line followed by a period and a space (e.g., "1. ")
    letters = re.split(r'(?<=\n)\d+\.\s', text)
    return [letter.strip() for letter in letters if letter.strip()]

def save_letters_to_files(letters, output_folder):
    """Save each letter into a separate text file."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for i, letter in enumerate(letters, start=1):
        file_path = os.path.join(output_folder, f"letter_{i}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(letter)
    print(f"Letters saved to folder: {output_folder}")

if __name__ == "__main__":
    base_path = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters"
    
    input_path = os.path.join(base_path, "extracted_text.txt")
    output_folder = os.path.join(base_path, "divided_letters")
    
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()
    
    letters = split_letters(text)
    save_letters_to_files(letters, output_folder)
