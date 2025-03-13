import pandas as pd
import os
import re

# Set input and output directories
input_dir = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/database/output"
output_dir = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/database/cleaned"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Function to fix common OCR errors in words
def fix_ocr_errors(text):
    if isinstance(text, str):
        text = re.sub(r"(?<!\d)10(?!\d)", "io", text)  # Fix "10" → "io" in words
        text = re.sub(r"(?<!\d)1(?!\d)", "i", text)    # Fix "1" → "i" in words
        text = re.sub(r"\bm\b", "in", text)            # Fix "m" → "in" when a standalone word
    return text

# Loop through all CSV files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".csv") and not filename.endswith("_cleaned.csv"):
        csv_path = os.path.join(input_dir, filename)
        output_cleaned_csv = os.path.join(output_dir, filename.replace(".csv", "_cleaned.csv"))

        print(f"🔄 Processing {filename}...")

        # Load CSV with better error handling
        try:
            df = pd.read_csv(csv_path, sep=",", engine="python", on_bad_lines="warn")
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
            continue  # Skip this file and move to the next

        # Trim spaces from all text columns
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

        # Standardize Name Formatting: Capitalize first letters (excluding fully uppercase names)
        df["Name"] = df["Name"].apply(lambda x: x.title() if x.islower() else x)

        # Apply OCR corrections to Name and Description columns (NOT Letters)
        df["Name"] = df["Name"].apply(fix_ocr_errors)
        df["Description"] = df["Description"].apply(fix_ocr_errors)

        # Ensure letter numbers are formatted correctly (remove spaces, keep only valid numbers)
        df["Letters"] = df["Letters"].astype(str).str.replace(r"\s+", "", regex=True).str.replace(r",\s*", ",", regex=True)

        # Save the cleaned CSV in the new folder
        df.to_csv(output_cleaned_csv, index=False, sep=",", quoting=1)  # Ensures proper quoting

        print(f"✅ Cleaned file saved as {output_cleaned_csv}")

print("🎉 All files have been processed and saved in the 'cleaned' folder!")