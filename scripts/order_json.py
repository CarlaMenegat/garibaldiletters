import json
from collections import OrderedDict
import sys
from pathlib import Path

def ordenar_dicionario_json(caminho_entrada, caminho_saida=None):
    """
    Lê um arquivo JSON contendo um dicionário, ordena suas chaves alfabeticamente
    e salva o resultado em outro arquivo.

    :param caminho_entrada: Caminho do arquivo JSON original
    :param caminho_saida: Caminho do arquivo onde salvar o JSON ordenado (opcional)
    """
    caminho_entrada = Path(caminho_entrada)
    
    if not caminho_entrada.exists():
        print(f"Erro: Arquivo '{caminho_entrada}' não encontrado.")
        return

    # Nome de saída padrão
    if caminho_saida is None:
        caminho_saida = caminho_entrada.with_name(f"{caminho_entrada.stem}_ordenado.json")
    else:
        caminho_saida = Path(caminho_saida)

    try:
        with open(caminho_entrada, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        if not isinstance(dados, dict):
            print("Erro: O conteúdo do arquivo JSON não é um dicionário.")
            return

        dados_ordenados = OrderedDict(sorted(dados.items()))

        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(dados_ordenados, f, ensure_ascii=False, indent=2)

        print(f"Dicionário ordenado salvo em: {caminho_saida}")

    except json.JSONDecodeError as e:
        print(f"Erro de leitura JSON: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

# Exemplo de uso: python script.py entrada.json [saida.json]
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python script.py caminho_entrada.json [caminho_saida.json]")
    else:
        caminho_entrada = sys.argv[1]
        caminho_saida = sys.argv[2] if len(sys.argv) > 2 else None
        ordenar_dicionario_json(caminho_entrada, caminho_saida)