import json
import os
import re

PERICOPAS_DIR = r"C:\own\alejandria\prods\bookdc\pericopas"
JSON_FILE = r"C:\own\alejandria\data\scripture_structure\pericopae.json"

def get_pericopes_from_md(filepath):
    pericopes = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # Pattern: | Title | Start-End |
        matches = re.findall(r'\| (.*?) \| (\d+)(?:-(\d+))? \|', content)
        for match in matches:
            title = match[0].strip()
            if title.lower() == "titulo": continue # Skip header
            v_start = int(match[1])
            v_end = int(match[2]) if match[2] else v_start
            pericopes.append((v_start, v_end, title))
    return pericopes

def main():
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found")
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return

    # Map section -> chapter_mysql_id
    section_to_chapter_id = {}
    for entry in data:
        if entry.get('volume_slug') == 'dc' and entry.get('book_slug') == 'sections':
            section_to_chapter_id[entry['chapter_num']] = entry['chapter_mysql_id']

    # Filter out existing dc/sections
    non_dc_data = [e for e in data if not (e.get('volume_slug') == 'dc' and e.get('book_slug') == 'sections')]

    # Track max mysql_id to assign new ones
    # We will use a safe range or just re-index?
    # Let's find the max mysql_id in non_dc_data
    max_mysql_id = max(e['mysql_id'] for e in non_dc_data) if non_dc_data else 0

    # Parse all MD files
    md_files = [f for f in os.listdir(PERICOPAS_DIR) if f.startswith("Esquema de DyC") and f.endswith(".md")]
    
    def get_section_num(filename):
        m = re.search(r'DyC (\d+)', filename)
        return int(m.group(1)) if m else 999
    
    md_files.sort(key=get_section_num)

    added_pericopes = []
    for filename in md_files:
        section_num = get_section_num(filename)
        filepath = os.path.join(PERICOPAS_DIR, filename)
        pericopes = get_pericopes_from_md(filepath)
        
        chapter_mysql_id = section_to_chapter_id.get(section_num, section_num + 1428)
        
        for v_start, v_end, title in pericopes:
            max_mysql_id += 1
            new_entry = {
                "mysql_id": max_mysql_id,
                "chapter_mysql_id": chapter_mysql_id,
                "corpus_path": f"dc/sections/{section_num}.txt",
                "volume_slug": "dc",
                "book_slug": "sections",
                "chapter_num": section_num,
                "verse_start": v_start,
                "verse_end": v_end,
                "name_es": title,
                "name_en": "" # Leave English empty as requested in previous similar tasks or just use title
            }
            added_pericopes.append(new_entry)

    # Combine and sort
    final_data = non_dc_data + added_pericopes
    final_data.sort(key=lambda x: x['mysql_id'])

    # Validate no duplicate mysql_id
    ids = [e['mysql_id'] for e in final_data]
    if len(ids) != len(set(ids)):
        print("Warning: Duplicate mysql_ids detected. Re-indexing...")
        for i, entry in enumerate(final_data):
            entry['mysql_id'] = i + 1

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"Successfully updated {len(added_pericopes)} pericopes in {JSON_FILE}")

if __name__ == "__main__":
    main()
