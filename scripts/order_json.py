import json
from collections import OrderedDict
from pathlib import Path

# Caminho do arquivo de entrada
caminho_entrada = Path("/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/database/dicionario_biografico.json")

# Caminho do arquivo de saída
caminho_saida = caminho_entrada.with_name("dicionario_biografico_ordered.json")

def ordenar_dicionario_json(caminho_entrada, caminho_saida):
    try:
        with open(caminho_entrada, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        if not isinstance(dados, dict):
            raise ValueError("O conteúdo do JSON precisa ser um dicionário na raiz.")

        dados_ordenados = OrderedDict(sorted(dados.items()))

        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(dados_ordenados, f, ensure_ascii=False, indent=2)

        print(f"Dicionário ordenado salvo em: {caminho_saida}")

    except json.JSONDecodeError as e:
        print(f"Erro ao ler o JSON: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

# Executa a função
ordenar_dicionario_json(caminho_entrada, caminho_saida)