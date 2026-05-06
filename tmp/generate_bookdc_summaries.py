import os
import json
import urllib.request
from pathlib import Path
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b-instruct-q4_K_M"

def call_ollama(prompt):
    data = {"model": MODEL, "prompt": prompt, "stream": False, "format": "json"}
    req = urllib.request.Request(OLLAMA_URL, 
                                 data=json.dumps(data).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "")
    except urllib.error.HTTPError as e:
        print("HTTP Error calling Ollama:", e.code, e.read().decode())
        return ""
    except Exception as e:
        print("Error calling Ollama:", e)
        return ""

def process_section(section_id, txt_path, meta_path, out_path):
    if out_path.exists():
        print(f"Skipping {section_id}, already exists.")
        return

    print(f"Processing {section_id}...")
    txt_content = txt_path.read_text(encoding="utf-8")
    meta_content = ""
    if meta_path.exists():
        meta_data = json.loads(meta_path.read_text(encoding="utf-8"))
        summary = meta_data.get("summary", "")
        study_intro = meta_data.get("study_intro", "")
        meta_content = f"Sumario original: {summary}\nIntroducción de estudio: {study_intro}"
    
    prompt = f"""
Eres un experto en historia y escrituras. Analiza el siguiente texto de la sección {section_id} de Doctrina y Convenios.
DEBES escribir tu respuesta ÚNICAMENTE en ESPAÑOL. No incluyas explicaciones en otro idioma.
Tu tarea es devolver un objeto JSON estrictamente formateado con la siguiente estructura y propiedades exactas, sin agregar NADA MÁS fuera del JSON:

{{
  "titulo": "El título histórico o consagrado de la sección (ej: 'El Prefacio', 'La Hoja de Olivo', 'La Visión', 'La Palabra de Sabiduría'). Si no tiene uno general, extrae de la metadata su título descriptivo",
  "recibido_por": "Quién recibió la revelación (ejemplo: José Smith el Profeta)",
  "fecha": "Fecha en la que fue recibida",
  "lugar": "Lugar en el que fue recibida",
  "palabra_clave": "Una palabra, frase o concepto único distintivo para la sección (ej. para la sección 1 podría ser 'La voz de amonestación')",
  "versiculos": 0,
  "introduccion": "Un sólo párrafo breve e introductorio",
  "objetivo": "Un sólo párrafo breve y comprensivo del objetivo general del texto",
  "antecedentes_contexto": "Un párrafo sobre los antecedentes y contexto cronológico o histórico",
  "tema_principal": "El tema principal, conceptualizado a forma de una taxonomía abstracta y reflexiva",
  "subtemas": ["Subtema 1", "Subtema 2", "Subtema 3"],
  "eventos": ["Evento del mundo real 1", "Evento del mundo real 2"]
}}

Reglas:
1. RESPONDE SOLAMENTE CON EL JSON. NO ESCRIBAS ESPACIOS NI TEXTO INTRODUCTORIO.
2. TODO EL CONTENIDO DEBE ESTAR STRICTAMENTE EN ESPAÑOL.
3. El número de versículos infiérelos del texto.
4. En "eventos" debes deducir a partir del encabezado (metadata) cuáles fueron las circunstancias que rodearon la sección. Menciona hechos históricos concretos contextuales. NO incluyas eventos escatológicos o profecías del texto.
5. El "tema_principal" y los "subtemas" deben formar una taxonomía temática bien pensada y rigurosa, no solo palabras aleatorias.

Aquí tienes los datos:
=== METADATA ===
{meta_content}

=== TEXTO ===
{txt_content}
"""
    response = call_ollama(prompt)
    if not response:
        print(f"Failed to get response for {section_id}")
        return
    
    try:
        # Extraer JSON limpio de la respuesta
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"Successfully wrote {out_path.name}")
        else:
            print(f"Could not parse JSON for {section_id}")
    except Exception as e:
        print(f"Error parsing JSON for {section_id}:", e)
        print("Raw response:", response)

def main():
    base_dir = Path("c:/own/alejandria")
    secciones_dir = base_dir / "corpus/es/scriptures/dc/secciones"
    do_dir = base_dir / "corpus/es/scriptures/dc/declaraciones-oficiales"
    out_dir = base_dir / "prods/bookdc/section_summaries"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Procesar secciones 1-138
    for i in range(1, 139):
        sec_id = f"{i:03d}"
        txt = secciones_dir / f"{i}.txt"
        meta = secciones_dir / f"{i}.meta.json"
        out = out_dir / f"sumario_dyc_{sec_id}.json"
        if txt.exists():
            process_section(sec_id, txt, meta, out)
            
    # Procesar declaraciones oficiales
    for i in range(1, 3):
        sec_id = f"do{i}"
        txt = do_dir / f"{i}.txt"
        meta = do_dir / f"{i}.meta.json"
        out = out_dir / f"sumario_dyc_{sec_id}.json"
        if txt.exists():
            process_section(sec_id, txt, meta, out)

if __name__ == "__main__":
    main()
