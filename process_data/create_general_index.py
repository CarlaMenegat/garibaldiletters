import os
import json
import re
from collections import defaultdict

# Caminhos
base_path = '/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/final_clean_index'
output_path = '/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/database'

# Dicionário biográfico
bio_dict = {}
id_ocorrencias = defaultdict(int)  # Para lidar com homônimos

# Função para gerar ID simples e legível
def generate_human_id(sobrenome, nome):
    primeiro_sobrenome = sobrenome.strip().split()[0].lower()
    primeiro_nome = nome.strip().split()[0].lower() if nome else "anonimo"
    base_id = f"{primeiro_sobrenome}-{primeiro_nome}"
    id_ocorrencias[base_id] += 1
    if id_ocorrencias[base_id] > 1:
        return f"{base_id}-{id_ocorrencias[base_id]}"
    return base_id

# Loop pelos arquivos
for volume in range(1, 15):
    file_path = os.path.join(base_path, f"extracted_vol{volume}_index.txt")
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            # Tenta separar páginas
            match_paginas = re.search(r'(\d{1,3}(?:,\s*\d{1,3})*)$', line)
            if not match_paginas:
                continue

            paginas_str = match_paginas.group(1)
            paginas = [int(p.strip()) for p in paginas_str.split(',') if int(p.strip()) <= 500]
            if not paginas:
                continue

            texto_principal = line[:match_paginas.start()].strip().rstrip(',')

            # Divide usando vírgulas
            partes = [p.strip() for p in texto_principal.split(',', maxsplit=2)]

            if len(partes) == 3:
                sobrenome, nome, descricao = partes
            elif len(partes) == 2:
                sobrenome = partes[0]
                nome = ''
                descricao = partes[1]
            else:
                continue

            nome_completo = f"{sobrenome}, {nome}".strip(', ').strip()
            unique_id = generate_human_id(sobrenome, nome)

            if nome_completo not in bio_dict:
                bio_dict[nome_completo] = {
                    "id": unique_id,
                    "descriptions": [],
                    "occurrences": []
                }

            if descricao and descricao not in bio_dict[nome_completo]["descriptions"]:
                bio_dict[nome_completo]["descriptions"].append(descricao)

            bio_dict[nome_completo]["occurrences"].append({
                "volume": volume,
                "pages": paginas
            })

# Ordenar o dicionário por nome completo (chave)
bio_dict_ordenado = dict(sorted(bio_dict.items(), key=lambda x: x[0]))

# Exportar JSON
json_output_path = os.path.join(output_path, 'dicionario_biografico.json')
with open(json_output_path, 'w', encoding='utf-8') as json_file:
    json.dump(bio_dict_ordenado, json_file, indent=2, ensure_ascii=False)

print(f"✅ Dicionário biográfico exportado em ordem alfabética para {json_output_path}")
