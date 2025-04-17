import os
import json
import xml.etree.ElementTree as ET

# Diretório onde estão os XMLs das cartas
INPUT_DIR = 'letters'
OUTPUT_FILE = 'letters_order.json'

TEI_NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

def extract_metadata(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    date_el = root.find('.//tei:date', TEI_NS)
    place_el = root.find('.//tei:placeName', TEI_NS)

    if date_el is None or 'when' not in date_el.attrib:
        return None  # ignorar se não tiver data

    return {
        'file': os.path.basename(file_path),
        'date': date_el.attrib['when'],
        'place': place_el.text.strip() if place_el is not None else ''
    }

def main():
    letters = []

    for filename in os.listdir(INPUT_DIR):
        # Ignora traduções
        if filename.endswith('.xml') and not filename.endswith('_en.xml'):
            path = os.path.join(INPUT_DIR, filename)
            data = extract_metadata(path)
            if data:
                letters.append(data)

    # Ordenar por data
    letters.sort(key=lambda x: x['date'])

    # Salvar como JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(letters, f, indent=2, ensure_ascii=False)

    print(f'{len(letters)} cartas (sem traduções) exportadas para {OUTPUT_FILE}')

if __name__ == '__main__':
    main()