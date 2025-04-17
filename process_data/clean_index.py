import os
import re

# 📌 Diretórios de entrada e saída
input_dir = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/extracted_index"
output_dir = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/garibaldiletters/final_clean_index"

# 📌 Criar diretórios se não existirem
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# 📌 Função para corrigir erros comuns de OCR
def correct_ocr_errors(text):
    text = re.sub(r'(?<!\d)10(?!\d)', 'io', text)  # Corrige "10" por "io"
    text = re.sub(r'(?<!\d)01(?!\d)', 'oi', text)  # Corrige "01" por "oi"
    text = re.sub(r'(?<!\d)1(?!\d)', 'i', text)  # Corrige "1" por "i"
    text = re.sub(r'(?<!\w)6(?!\w)', 'Ó', text)  # Corrige "6" por "Ó" maiúsculo
    text = re.sub(r'(?<!\w)6', 'ó', text)  # Corrige "6" por "ó" minúsculo quando no meio da palavra
    text = re.sub(r'(?<!\w)w(?!\w)', 'io', text)  # Corrige "w" por "io"
    text = re.sub(r'\bm\b', 'in', text)  # Corrige "m" por "in"
    text = re.sub(r'(?<![A-Za-z])m(?![A-Za-z])', 'in', text)  # Corrige "m" por "in" dentro de palavras
    text = re.sub(r'(?<!\w)r(?!\w)', 'Í', text)  # Corrige "r" por "Í"
    text = re.sub(r'(?<!\w)f(?!\w)', 'í', text)  # Corrige "f" por "í"
    text = re.sub(r'\b([A-ZÁÉÍÓÚÑÜ]{2,})[a-z]([A-ZÁÉÍÓÚÑÜ]*)\b', lambda m: m.group(1) + m.group(2).upper(), text)  # Corrige nomes com letras minúsculas no meio
    text = re.sub(r'([A-ZÁÉÍÓÚÑÜ]),\s*([a-záéíóúñü])', lambda m: f"{m.group(1)}, {m.group(2).upper()}", text)  # Corrige iniciais minúsculas após vírgulas
    text = re.sub(r'\b(\w+)-\s+(\w+)\b', r'\1\2', text)  # Remove hifens em palavras divididas
    text = re.sub(r',\s*,+', ',', text)  # Remove múltiplas vírgulas
    text = text.strip(', ')  # Remove vírgulas e espaços extras
    return text

# 📌 Função para rejuntar linhas quebradas
def fix_broken_lines(text):
    lines = text.split('\n')
    fixed_lines = []
    
    for i in range(len(lines)):
        if i > 0 and re.match(r'\d{1,3}$', lines[i].strip()):  # Linha apenas com número
            fixed_lines[-1] += ", " + lines[i].strip()  # Junta ao nome anterior
        else:
            fixed_lines.append(lines[i])
    
    return '\n'.join(fixed_lines)

# 📌 Processar todos os arquivos na pasta de entrada
if os.path.exists(input_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Aplicar as correções
            text = correct_ocr_errors(text)
            text = fix_broken_lines(text)
            
            # Salvar o texto limpo
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            print(f"✅ Texto limpo salvo: {output_path}")
else:
    print(f"❌ ERRO: O diretório de entrada '{input_dir}' não existe. Verifique o caminho e tente novamente.")