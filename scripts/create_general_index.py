import os
import re
import json

# 📌 Diretórios de entrada e saída
input_dir = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/final_clean_index"
output_json = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/database/biographical_data.json"

# 📌 Função para extrair os dados do índice limpo
def extract_data_from_cleaned_text(file_path, volume):
    """Extrai nome, biografia e páginas de um índice limpo."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    entries = []
    current_entry = {"name": "", "bio_note": "", "pages": [], "volume": volume}
    
    for line in lines:
        line = line.strip()
        
        # Se a linha estiver vazia, pula
        if not line:
            continue
        
        # Expressão regular para capturar nome, bio e páginas
        match = re.match(r"^([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ,\s-]*)(.*?)(\d+(?:,\s*\d+)*)?$", line)
        
        if match:
            name = match.group(1).strip().rstrip(',')  # Remove vírgula final se houver
            bio = match.group(2).strip()
            pages = match.group(3)
            
            # Converte números das páginas em uma lista de inteiros
            page_numbers = [int(n) for n in pages.split(',')] if pages else []
            
            # Se já tivermos uma entrada em progresso, salvamos antes de iniciar a nova
            if current_entry["name"]:
                entries.append(current_entry)
                current_entry = {"name": "", "bio_note": "", "pages": [], "volume": volume}
            
            # Atualiza a nova entrada
            current_entry["name"] = name
            current_entry["bio_note"] = bio
            current_entry["pages"] = page_numbers
        
        else:
            # Se não for uma nova entrada, é continuação da bio anterior
            current_entry["bio_note"] += " " + line.strip()
    
    # Adiciona a última entrada se houver
    if current_entry["name"]:
        entries.append(current_entry)
    
    return entries

# 📌 Processar todos os arquivos na pasta de entrada
all_entries = []
if os.path.exists(input_dir):
    for filename in os.listdir(input_dir):
        if filename.startswith("extracted_vol") and filename.endswith(".txt"):
            volume = int(re.search(r'vol(\d+)', filename).group(1))  # Extrai o número do volume
            file_path = os.path.join(input_dir, filename)
            entries = extract_data_from_cleaned_text(file_path, volume)
            all_entries.extend(entries)
    
    # Salvar em JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Dados biográficos extraídos e salvos em: {output_json}")
else:
    print(f"❌ ERRO: O diretório de entrada '{input_dir}' não existe. Verifique o caminho e tente novamente.")
