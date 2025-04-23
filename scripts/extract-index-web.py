import os
import json
import xml.etree.ElementTree as ET

INPUT_DIR = 'letters'
OUTPUT_FILE = 'letters_index.json'
TEI_NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

def extract_metadata(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        header = root.find('.//tei:teiHeader', TEI_NS)

        # Skip translations
        if file_path.endswith('_en.xml'):
            return None

        title_el = header.find('.//tei:titleStmt/tei:title', TEI_NS)
        date_el = header.find('.//tei:correspDesc//tei:date', TEI_NS)
        origin_place_el = header.find('.//tei:correspAction[@type="sent"]/tei:placeName', TEI_NS)
        dest_place_el = header.find('.//tei:correspAction[@type="received"]/tei:placeName', TEI_NS)
        sender_el = header.find('.//tei:correspAction[@type="sent"]/tei:persName', TEI_NS)
        recipient_el = header.find('.//tei:correspAction[@type="received"]/*[1]', TEI_NS)

        # Theme extraction
        theme_el = header.findall('.//tei:textClass//tei:term', TEI_NS)
        theme_list = [t.attrib.get('ana', '').strip() for t in theme_el if t.attrib.get('ana')]
        theme = ', '.join(theme_list)

        manifest_el = header.find('.//tei:ptr[@target][1]', TEI_NS)
        manifest = manifest_el.attrib['target'] if manifest_el is not None else ''

        # Thumbnail extraction from <ref type="thumbnail">
        thumb_el = header.find('.//tei:ref[@type="thumbnail"]', TEI_NS)
        thumbnail = thumb_el.attrib['target'] if thumb_el is not None else ''

        return {
            'file': os.path.basename(file_path),
            'title': title_el.text.strip() if title_el is not None else '',
            'date': date_el.attrib.get('when', '') if date_el is not None else '',
            'place': origin_place_el.text.strip() if origin_place_el is not None else '',
            'destPlace': dest_place_el.text.strip() if dest_place_el is not None else '',
            'sender': sender_el.text.strip() if sender_el is not None else '',
            'recipient': recipient_el.text.strip() if recipient_el is not None else '',
            'manifest': manifest,
            'thumbnail': thumbnail,
            'theme': theme
        }

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    letters = []

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith('.xml') and not filename.endswith('_en.xml'):
            path = os.path.join(INPUT_DIR, filename)
            data = extract_metadata(path)
            if data:
                letters.append(data)

    letters.sort(key=lambda x: x['date'])

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(letters, f, indent=2, ensure_ascii=False)

    print(f'{len(letters)} letters exported to {OUTPUT_FILE}')

if __name__ == '__main__':
    main()