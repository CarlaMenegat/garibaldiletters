import json
from pathlib import Path
from lxml import etree

def convert_to_xml(letter_text, metadata, letter_number):
    tei = etree.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    
    teiHeader = etree.SubElement(tei, "teiHeader")
    fileDesc = etree.SubElement(teiHeader, "fileDesc")
    titleStmt = etree.SubElement(fileDesc, "titleStmt")
    etree.SubElement(titleStmt, "title").text = f"Letter {letter_number}"
    
    profileDesc = etree.SubElement(teiHeader, "profileDesc")
    
    for key, value in metadata.items():
        if key == "date":
            correspDesc = etree.SubElement(profileDesc, "correspDesc")
            etree.SubElement(correspDesc, "dateSent").text = value
        elif key in ["sender", "recipient"]:
            particDesc = etree.SubElement(profileDesc, "particDesc")
            person = etree.SubElement(particDesc, "person")
            etree.SubElement(person, "persName").text = value
            etree.SubElement(person, "role").text = key
        elif key == "place":
            settingDesc = etree.SubElement(profileDesc, "settingDesc")
            etree.SubElement(settingDesc, "name", type="place").text = value
        elif key == "language":
            langUsage = etree.SubElement(profileDesc, "langUsage")
            etree.SubElement(langUsage, "language", ident=value).text = value
    
    text = etree.SubElement(tei, "text")
    body = etree.SubElement(text, "body")
    
    paragraphs = letter_text.split('\n\n')
    for paragraph in paragraphs:
        etree.SubElement(body, "p").text = paragraph.strip()
    
    return etree.tostring(tei, pretty_print=True, encoding="unicode")

def process_letters(input_directory, metadata_file, output_directory):
    # Load metadata
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata_list = json.load(f)
    
    # Ensure the output directory exists
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    
    for i, metadata in enumerate(metadata_list, 1):
        letter_file = Path(input_directory) / metadata['file_name']
        
        with open(letter_file, 'r', encoding='utf-8') as f:
            letter_text = f.read()
        
        xml_content = convert_to_xml(letter_text, metadata, i)
        
        output_file = Path(output_directory) / f"letter_{i}.xml"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"Processed Letter {i}: XML file created at {output_file}")

# Directory paths
input_directory = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/divided_letters"
metadata_file = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/metadata/metadata.json"
output_directory = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/tei_letters"

# Run the processing function
process_letters(input_directory, metadata_file, output_directory)
