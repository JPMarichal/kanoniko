import re
import os

INPUT_FILE = r"C:\own\alejandria\prods\bookdc\namelist_with_passages.md"
OUTPUT_FILE = r"C:\own\alejandria\prods\bookdc\namelist_per_section.md"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found")
        return

    section_to_names = {} # dict: section_str -> set of names
    current_name = None

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            # Name header
            if line.startswith('## '):
                current_name = line[3:].strip()
                continue
            
            # Passage line
            if line.startswith('- DyC ') or line.startswith('- Declaración Oficial '):
                # Extract section parts. Handle multiple sections if comma separated in line?
                # Actually, the file seems to have one per line mostly.
                # Regex to find numbers
                sections = re.findall(r'(DyC|Declaración Oficial) (\d+)', line)
                for prefix, num in sections:
                    key = f"{prefix} {int(num)}"
                    if key not in section_to_names:
                        section_to_names[key] = set()
                    if current_name:
                        section_to_names[key].add(current_name)

    # Sorting
    def sort_key(s):
        match = re.search(r'(\d+)', s)
        num = int(match.group(1)) if match else 0
        if "Declaración" in s:
            return 200 + num # Put declarations at the end
        return num

    sorted_sections = sorted(section_to_names.keys(), key=sort_key)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Relación de Nombres por Sección de DyC\n\n")
        f.write("Esta relación es una vista inversa de `namelist_with_passages.md`.\n\n")
        
        for section in sorted_sections:
            f.write(f"## {section}\n")
            names = sorted(list(section_to_names[section]))
            for name in names:
                f.write(f"- {name}\n")
            f.write("\n")

    print(f"Inverse namelist generated in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
