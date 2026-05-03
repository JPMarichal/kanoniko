#!/usr/bin/env python3
"""
Genera documentos de esquemas de perícopas para Doctrina y Convenios.
Crea un archivo markdown por sección con una tabla de perícopas.
Detecta errores (versículos sin perícopa) y los reporta en Errores.md.
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

# Rutas
PERICOPAE_FILE = r"c:\own\alejandria\data\scripture_structure\pericopae.json"
DC_DIR = r"c:\own\alejandria\corpus\es\scriptures\dc\secciones"
OUTPUT_DIR = r"c:\own\alejandria\prods\bookdc\pericopas"


def cargar_pericopas():
    """Carga el archivo pericopae.json y filtra las de DyC."""
    with open(PERICOPAE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filtrar perícopas de DyC (volume_slug="dc", book_slug="sections")
    dyc_pericopas = [
        p for p in data 
        if p.get('volume_slug') == 'dc' and p.get('book_slug') == 'sections'
    ]
    return dyc_pericopas


def obtener_versiculos_seccion(num_seccion):
    """Obtiene el número total de versículos en una sección leyendo el archivo de texto."""
    archivo = os.path.join(DC_DIR, f"{num_seccion}.txt")
    if not os.path.exists(archivo):
        return 0
    
    with open(archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
    
    max_versiculo = 0
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
        # Buscar número de versículo al inicio de la línea
        match = re.match(r'^(\d+)\s', linea)
        if match:
            num = int(match.group(1))
            max_versiculo = max(max_versiculo, num)
    
    return max_versiculo


def agrupar_por_seccion(pericopas):
    """Agrupa las perícopas por número de sección."""
    secciones = defaultdict(list)
    for p in pericopas:
        chapter_num = p.get('chapter_num')
        if chapter_num:
            secciones[chapter_num].append(p)
    
    # Ordenar perícopas dentro de cada sección por verse_start
    for sec in secciones:
        secciones[sec].sort(key=lambda x: x.get('verse_start', 0))
    
    return secciones


def detectar_errores(seccion_num, pericopas, total_versiculos):
    """Detecta versículos sin perícopa."""
    errores = []
    
    if total_versiculos == 0:
        errores.append(f"No se encontró archivo de texto para la sección {seccion_num}")
        return errores
    
    if not pericopas:
        errores.append(f"Sección {seccion_num}: No tiene perícopas definidas (versículos 1-{total_versiculos})")
        return errores
    
    # Verificar cobertura completa
    versiculos_cubiertos = set()
    for p in pericopas:
        start = p.get('verse_start', 0)
        end = p.get('verse_end', start)
        for v in range(start, end + 1):
            versiculos_cubiertos.add(v)
    
    # Detectar versículos faltantes
    faltantes = []
    for v in range(1, total_versiculos + 1):
        if v not in versiculos_cubiertos:
            faltantes.append(v)
    
    if faltantes:
        # Agrupar versículos consecutivos
        grupos = []
        inicio = faltantes[0]
        fin = faltantes[0]
        
        for v in faltantes[1:]:
            if v == fin + 1:
                fin = v
            else:
                if inicio == fin:
                    grupos.append(f"{inicio}")
                else:
                    grupos.append(f"{inicio}-{fin}")
                inicio = v
                fin = v
        
        # Agregar último grupo
        if inicio == fin:
            grupos.append(f"{inicio}")
        else:
            grupos.append(f"{inicio}-{fin}")
        
        errores.append(f"Sección {seccion_num}: Versículos sin perícopa: {', '.join(grupos)}")
    
    # Verificar superposiciones
    for i, p1 in enumerate(pericopas):
        for p2 in pericopas[i+1:]:
            # Si hay superposición
            if (p1['verse_start'] <= p2['verse_end'] and p2['verse_start'] <= p1['verse_end']):
                errores.append(
                    f"Sección {seccion_num}: Superposición de perícopas - "
                    f"'{p1['name_es']}' (vs {p1['verse_start']}-{p1['verse_end']}) y "
                    f"'{p2['name_es']}' (vs {p2['verse_start']}-{p2['verse_end']})"
                )
    
    return errores


def formatear_versiculos(verse_start, verse_end):
    """Formatea el rango de versículos."""
    if verse_start == verse_end:
        return f"{verse_start}"
    return f"{verse_start}-{verse_end}"


def generar_tabla_markdown(pericopas):
    """Genera la tabla markdown con las perícopas."""
    lineas = [
        "| Titulo | Versículos |",
        "|--------|------------|"
    ]
    
    for p in pericopas:
        titulo = p.get('name_es', '').strip()
        versiculos = formatear_versiculos(p.get('verse_start', 0), p.get('verse_end', 0))
        lineas.append(f"| {titulo} | {versiculos} |")
    
    return '\n'.join(lineas)


def main():
    # Crear directorio de salida si no existe
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Cargando perícopas...")
    pericopas = cargar_pericopas()
    print(f"Total de perícopas de DyC: {len(pericopas)}")
    
    # Agrupar por sección
    secciones = agrupar_por_seccion(pericopas)
    print(f"Secciones encontradas: {len(secciones)}")
    
    # Procesar cada sección del 1 al 138
    todos_errores = []
    
    for sec_num in range(1, 139):
        # Obtener perícopas de esta sección
        pericopas_sec = secciones.get(sec_num, [])
        
        # Obtener número total de versículos
        total_versiculos = obtener_versiculos_seccion(sec_num)
        
        # Detectar errores
        errores = detectar_errores(sec_num, pericopas_sec, total_versiculos)
        todos_errores.extend(errores)
        
        # Generar archivo markdown
        num_formateado = f"{sec_num:03d}"
        archivo_salida = os.path.join(OUTPUT_DIR, f"Esquema de DyC {num_formateado}.md")
        
        if pericopas_sec:
            tabla = generar_tabla_markdown(pericopas_sec)
            contenido = f"# Esquema de Doctrina y Convenios {sec_num}\n\n{tabla}\n"
        else:
            contenido = f"# Esquema de Doctrina y Convenios {sec_num}\n\n*No hay perícopas definidas para esta sección.*\n"
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        if sec_num % 20 == 0 or sec_num == 138:
            print(f"  Procesadas {sec_num}/138 secciones...")
    
    # Generar archivo de errores
    archivo_errores = os.path.join(OUTPUT_DIR, "Errores.md")
    with open(archivo_errores, 'w', encoding='utf-8') as f:
        f.write("# Errores en Perícopas de Doctrina y Convenios\n\n")
        f.write("Este documento lista los problemas detectados en las perícopas de DyC.\n\n")
        
        if todos_errores:
            f.write("## Problemas Detectados\n\n")
            for error in todos_errores:
                f.write(f"- {error}\n")
            f.write(f"\n**Total de problemas: {len(todos_errores)}**\n")
        else:
            f.write("No se detectaron problemas en las perícopas.\n")
    
    print(f"\n✓ Completado!")
    print(f"  - Archivos generados: 138")
    print(f"  - Problemas detectados: {len(todos_errores)}")
    print(f"  - Directorio: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
