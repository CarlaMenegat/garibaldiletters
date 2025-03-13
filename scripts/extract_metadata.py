import re
from pathlib import Path
from lingua import Language, LanguageDetectorBuilder
import spacy
import json

# Load spaCy models for Named Entity Recognition (NER)
nlp_models = {
    "spanish": spacy.load("es_core_news_sm"),
    "italian": spacy.load("it_core_news_sm"),
    "french": spacy.load("fr_core_news_sm"),
    "portuguese": spacy.load("pt_core_news_sm")
}

# Configure Lingua for language detection
detector = LanguageDetectorBuilder.from_languages(
    Language.SPANISH, Language.ITALIAN, Language.FRENCH, Language.PORTUGUESE
).build()

def detect_language_with_lingua(text):
    """Detect the language of the given text using Lingua."""
    language = detector.detect_language_of(text)
    return language.name.lower() if language else "unknown"

def extract_date(text):
    """
    Extract date from text using regex patterns.
    Supports various date formats in different languages.
    """
    date_patterns = [
        r'\b\d{1,2}\s+(?:de\s+)?[A-Za-zç]+\s+(?:de\s+)?\d{4}\b',  # e.g., 27 de Junho de 1837
        r'\b[A-Za-zç]+\s+\d{1,2},?\s+\d{4}\b',  # e.g., June 27, 1837
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # e.g., 27/06/1837
        r'\b\d{1,2}-\d{1,2}-\d{2,4}\b'   # e.g., 27-06-1837
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()
    return "Unknown"

def extract_place(text, language):
    # Common regex pattern for detecting locations in multiple languages
    place_pattern = r"^([A-ZÁÉÍÓÚÜÀÈÌÒÙÂÊÎÔÛÇ][a-záéíóúüàèìòùâêîôûç]+(?: [A-ZÁÉÍÓÚÜÀÈÌÒÙÂÊÎÔÛÇa-záéíóúüàèìòùâêîôûç]+)*)[,;]"

    # Searching for the place in the first three lines
    first_lines = text.split("\n")[:3]
    for line in first_lines:
        match = re.match(place_pattern, line.strip())
        if match:
            return match.group(1)  # Return the matched place name

    # If regex fails, fallback to spaCy NER
    if language not in nlp_models:
        return "Unknown"
    
    nlp = nlp_models[language]
    doc = nlp(text[:500])  # Analyze only the first 500 characters
    
    for ent in doc.ents:
        if ent.label_ in ["LOC", "GPE"]:  # Location or geopolitical entity
            return ent.text
    return "Unknown"

def extract_sender():
    """Return the fixed sender name: Giuseppe Garibaldi."""
    return "Giuseppe Garibaldi"

def extract_recipient(text):
    """
    Extract recipient from the first line of the text.
    Removes common prefixes and returns 'Unknown' if the line is too long.
    """
    lines = text.strip().split('\n')
    if lines:
        first_line = lines[0].strip()
        # Remove common prefixes
        prefixes = ['A', 'To', 'Para', 'Al', 'Alla', 'Ad' ]
        for prefix in prefixes:
            if first_line.startswith(prefix):
                first_line = first_line[len(prefix):].strip()
        return first_line if len(first_line) < 50 else "Unknown"
    return "Unknown"

def extract_metadata(letter_text, letter_number):
    """
    Extract metadata (sender, recipient, date, place) from letter text.
    """
    language = detect_language_with_lingua(letter_text)
    
    date = extract_date(letter_text)
    place = extract_place(letter_text, language)
    
    sender = extract_sender()
    recipient = extract_recipient(letter_text)
    
    return {
        "letter_number": letter_number,
        "sender": sender,
        "recipient": recipient,
        "date": date,
        "place": place,
        "language": language
    }

def extract_letter_number(filename):
    """
    Extract the letter number from the filename.
    Expects filenames in the format 'letter_X.txt' where X is the number.
    """
    match = re.match(r'letter_(\d+)\.txt', filename)
    if match:
        return int(match.group(1))
    return None

def process_letters(input_directory, output_directory):
    """
    Process all letters in the input directory and save metadata to a JSON file.
    """
    letter_files = sorted(Path(input_directory).glob('*.txt'))
    
    metadata_dict = {}
    
    for letter_file in letter_files:
        with open(letter_file, 'r', encoding='utf-8') as f:
            letter_text = f.read()
        
        letter_number = extract_letter_number(letter_file.name)
        if letter_number is None:
            print(f"Skipping file with invalid name format: {letter_file.name}")
            continue
        
        metadata = extract_metadata(letter_text, letter_number)
        
        metadata_dict[f"letter_{letter_number}"] = {
            "file_name": letter_file.name,
            **metadata
        }
        
        print(f"Processed Letter {letter_number}: {metadata}")
    
    # Ensure the output directory exists
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    
    # Save all metadata to a single JSON file in the output directory
    output_file = Path(output_directory) / "metadata.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata_dict, f, indent=4)
    
    print(f"Metadata saved to {output_file}")

# Directory paths
input_directory = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/divided_letters"
output_directory = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/metadata"

# Run the processing function
process_letters(input_directory, output_directory)

