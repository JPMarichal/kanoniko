#!/usr/bin/env python3
import json

with open(r'c:\own\alejandria\data\scripture_structure\pericopae.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filtrar solo DyC
pericopas = [p for p in data if p.get('volume_slug') == 'dc' and p.get('book_slug') == 'sections']

# Analizar longitudes
longitudes = [len(p['name_es']) for p in pericopas if p.get('name_es')]
longitudes_sorted = sorted(longitudes, reverse=True)

print(f'Total perícopas DyC: {len(pericopas)}')
print(f'\nLongitudes de títulos:')
print(f'  Media: {sum(longitudes)/len(longitudes):.1f} caracteres')
print(f'  Mediana: {sorted(longitudes)[len(longitudes)//2]} caracteres')
print(f'  Mínimo: {min(longitudes)} caracteres')
print(f'  Máximo: {max(longitudes)} caracteres')

print(f'\nTop 20 títulos más largos:')
pericopas_sorted = sorted(pericopas, key=lambda x: len(x['name_es']), reverse=True)
for p in pericopas_sorted[:20]:
    sec = p['chapter_num']
    name = p['name_es']
    print(f'DyC {sec:3d}: {len(name):3d} chars - "{name[:75]}{"..." if len(name)>75 else ""}"')

print(f'\nDistribución de longitudes:')
rangos = [(0, 50), (51, 75), (76, 100), (101, 120), (121, 150)]
for min_len, max_len in rangos:
    count = sum(1 for l in longitudes if min_len <= l <= max_len)
    pct = count / len(longitudes) * 100
    bar = '█' * int(pct / 2)
    print(f'  {min_len:3d}-{max_len:3d}: {count:3d} ({pct:5.1f}%) {bar}')

muy_largos = [l for l in longitudes if l > 100]
print(f'\nTítulos > 100 chars: {len(muy_largos)} ({len(muy_largos)/len(longitudes)*100:.1f}%)')

# Detectar truncados
print(f'\n=== Posibles títulos truncados (>95 chars y terminan abruptamente) ===')
sospechosos = []
terminaciones_sospechosas = [' y ', ' de ', ' el ', ' la ', ' a ', ' los', ' las', ' su ', ' se ', ' co', ' en ', ' al ', ' del ', ' con ']
for p in pericopas:
    name = p['name_es']
    if len(name) >= 95:
        # Verificar si termina con palabra incompleta
        ultimas_palabras = name.split()[-2:]  # Últimas 2 palabras
        ultima = name.split()[-1] if name.split() else ""
        
        # Si termina con preposición o artículo, o termina en medio de palabra
        termina_sospechoso = any(name.lower().endswith(t.strip()) for t in terminaciones_sospechosas)
        
        if termina_sospechoso or len(name) == 100 or len(name) == 98 or len(name) == 99:
            sospechosos.append((p['chapter_num'], name, len(name)))

for sec, name, length in sospechosos[:10]:
    print(f'DyC {sec}: [{length}] "{name}"')

print(f'\nTotal sospechosos: {len(sospechosos)}')
