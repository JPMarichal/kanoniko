#!/usr/bin/env python3
import json

with open(r'c:\own\alejandria\data\scripture_structure\pericopae.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filtrar perícopas de DyC
pericopas = [p for p in data if p.get('volume_slug') == 'dc']

# Buscar truncadas (terminan abruptamente)
truncadas = []
sospechosos = [' y glo', ' y g', ' la', ' de', ' el', ' a ', ' y ', ' en ', ' los', ' las', ' su', ' se ', ' co']

for p in pericopas:
    name = p.get('name_es', '')
    for s in sospechosos:
        if name.endswith(s) and len(name) > 50:
            truncadas.append((p['chapter_num'], name, len(name)))
            break

print(f'Títulos con posible truncamiento: {len(truncadas)}')
for sec, name, length in truncadas:
    print(f'DyC {sec}: "{name[:65]}..." ({length} chars)')
