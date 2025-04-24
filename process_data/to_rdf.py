import os
import json
from lxml import etree
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import DC, FOAF, RDF

# === CONFIGURAÇÃO ===

INPUT_FOLDER = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/letters"
OUTPUT_FOLDER = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/rdf"
PLACE_MAPPING_FILE = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/annotations/place_uri_mapping.json"

TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}

# === FUNÇÕES ===

def load_place_mapping(json_path):
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)

def extract_metadata(xml_path):
    tree = etree.parse(xml_path)
    root = tree.getroot()

    title = root.find(".//tei:title", namespaces=TEI_NS)
    author = root.find(".//tei:author", namespaces=TEI_NS)
    date = root.find(".//tei:correspDesc//tei:date", namespaces=TEI_NS)
    place = root.find(".//tei:placeName", namespaces=TEI_NS)

    return {
        "title": title.text.strip() if title is not None else "Sem título",
        "author": author.text.strip() if author is not None else "Desconhecido",
        "date": date.get("when") if date is not None else "Desconhecida",
        "place": place.text.strip() if place is not None else "Desconhecido",
        "place_code": place.get("key") if place is not None else None
    }

def generate_ttl(metadata, identifier, place_uri):
    return f"""@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix gn: <http://www.geonames.org/ontology#> .
@prefix ex: <http://example.org/correspondence/> .

ex:{identifier}
    a ex:Letter ;
    dc:title "{metadata['title']}" ;
    dc:creator "{metadata['author']}" ;
    dc:date "{metadata['date']}" ;
    dc:identifier "{identifier}" ;
    dc:coverage "{metadata['place']}" ;
    {"gn:locatedIn <" + place_uri + "> ;" if place_uri else ""}
    foaf:maker ex:{identifier}-author .

ex:{identifier}-author a foaf:Person ;
    foaf:name "{metadata['author']}" .
"""

def generate_jsonld(metadata, identifier, place_uri):
    data = {
        "@context": {
            "dc": "http://purl.org/dc/elements/1.1/",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "gn": "http://www.geonames.org/ontology#"
        },
        "@id": f"http://example.org/correspondence/{identifier}",
        "@type": "Letter",
        "dc:title": metadata["title"],
        "dc:creator": metadata["author"],
        "dc:date": metadata["date"],
        "dc:identifier": identifier,
        "dc:coverage": metadata["place"],
        "foaf:maker": {
            "@id": f"http://example.org/correspondence/{identifier}-author",
            "@type": "foaf:Person",
            "foaf:name": metadata["author"]
        }
    }
    if place_uri:
        data["gn:locatedIn"] = {"@id": place_uri}
    return data

def generate_rdfxml(metadata, identifier, place_uri):
    g = Graph()
    EX = Namespace("http://example.org/correspondence/")
    GN = Namespace("http://www.geonames.org/ontology#")

    letter_uri = EX[identifier]
    author_uri = EX[f"{identifier}-author"]

    g.add((letter_uri, RDF.type, EX.Letter))
    g.add((letter_uri, DC.title, Literal(metadata["title"])))
    g.add((letter_uri, DC.creator, Literal(metadata["author"])))
    g.add((letter_uri, DC.date, Literal(metadata["date"])))
    g.add((letter_uri, DC.identifier, Literal(identifier)))
    g.add((letter_uri, DC.coverage, Literal(metadata["place"])))
    if place_uri:
        g.add((letter_uri, GN.locatedIn, URIRef(place_uri)))
    g.add((letter_uri, FOAF.maker, author_uri))
    g.add((author_uri, RDF.type, FOAF.Person))
    g.add((author_uri, FOAF.name, Literal(metadata["author"])))

    return g.serialize(format="xml")

# === EXECUÇÃO PRINCIPAL ===

def main():
    import json

    place_mapping = load_place_mapping(PLACE_MAPPING_FILE)

    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".xml") and not filename.endswith("_en.xml"):
            xml_path = os.path.join(INPUT_FOLDER, filename)
            identifier = os.path.splitext(filename)[0]
            metadata = extract_metadata(xml_path)

            # Correção aqui ↓↓↓
            raw_code = metadata.get("place_code")
            place_code = raw_code.replace("#", "").upper() if raw_code else None
            place_uri = place_mapping.get(place_code) if place_code else None

            # TTL
            ttl_path = os.path.join(OUTPUT_FOLDER, f"{identifier}.ttl")
            with open(ttl_path, "w", encoding="utf-8") as f:
                f.write(generate_ttl(metadata, identifier, place_uri))

            # JSON-LD
            jsonld_path = os.path.join(OUTPUT_FOLDER, f"{identifier}.jsonld")
            with open(jsonld_path, "w", encoding="utf-8") as f:
                json.dump(generate_jsonld(metadata, identifier, place_uri), f, indent=2, ensure_ascii=False)

            # RDF/XML
            rdfxml_path = os.path.join(OUTPUT_FOLDER, f"{identifier}.rdf")
            with open(rdfxml_path, "w") as f:
                f.write(generate_rdfxml(metadata, identifier, place_uri))

            print(f"RDF gerado para {filename}")

if __name__ == "__main__":
    main()