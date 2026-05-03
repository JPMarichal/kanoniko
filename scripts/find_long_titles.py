#!/usr/bin/env python3
import os
import re
from pathlib import Path

PERICOPAS_DIR = r"c:\own\alejandria\prods\bookdc\pericopas"

def find_long_titles():
    """Identifica archivos con títulos > 75 caracteres."""
    long_titles = []
    
    for file in sorted(os.listdir(PERICOPAS_DIR)):
        if file.startswith('Esquema de DyC') and file.endswith('.md'):
            num = int(re.search(r'(\d+)\.md', file).group(1))
            filepath = os.path.join(PERICOPAS_DIR, file)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                if line.startswith('|') and 'Titulo' not in line and '---' not in line and line.strip() != '|':
                    # Extraer título (entre | y |)
                    parts = line.split('|')
                    if len(parts) >= 3:
                        title = parts[1].strip()
                        if len(title) > 75:
                            long_titles.append({
                                'file': file,
                                'section': num,
                                'title': title,
                                'length': len(title),
                                'full_line': line.strip()
                            })
    
    return long_titles

def main():
    long_titles = find_long_titles()
    
    print(f"Encontrados {len(long_titles)} títulos > 75 caracteres:")
    print("=" * 80)
    
    for item in sorted(long_titles, key=lambda x: x['section']):
        print(f"DyC {item['section']:3d}: [{item['length']:3d}] \"{item['title']}\"")
    
    print(f"\nTotal: {len(long_titles)} títulos para revisar")
    
    # Guardar lista para procesamiento
    with open(r'c:\own\alejandria\scripts\long_titles_to_fix.txt', 'w', encoding='utf-8') as f:
        for item in sorted(long_titles, key=lambda x: x['section']):
            f.write(f"{item['file']}|{item['section']}|{item['title']}|{item['length']}\n")
    
    print("Lista guardada en: long_titles_to_fix.txt")

if __name__ == "__main__":
    main()
