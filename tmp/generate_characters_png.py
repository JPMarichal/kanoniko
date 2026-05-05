import os
import re
from PIL import Image, ImageDraw, ImageFont

MD_FILE = r"C:\own\alejandria\prods\bookdc\namelist_per_section.md"
OUTPUT_DIR = r"C:\own\alejandria\prods\bookdc\personajes_x_seccion_png"

def parse_names(filepath):
    data = {}
    current_key = None
    if not os.path.exists(filepath): return data
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            rm_sec = re.match(r'##\s+(DyC|Declaración Oficial)\s+(\d+)', line, re.IGNORECASE)
            if rm_sec:
                prefix = rm_sec.group(1).lower()
                num = int(rm_sec.group(2))
                current_key = (prefix, num)
                data[current_key] = []
            elif line.startswith('- ') and current_key is not None:
                name = line[2:].strip()
                if name:
                    data[current_key].append(name)
    return data

def get_font(bold=False, size=18):
    font_path = "C:\\Windows\\Fonts\\segoeui.ttf"
    font_path_bold = "C:\\Windows\\Fonts\\segoeuib.ttf"
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        font_path_bold = "C:\\Windows\\Fonts\\arialbd.ttf"
    try:
        return ImageFont.truetype(font_path_bold if bold else font_path, size)
    except:
        return ImageFont.load_default()

def render_names(section_num, names, output_path):
    # Proporción para 5.3 x 7.5 cm (aprox 1:1.41)
    canvas_w = 530
    canvas_h = 750
    img = Image.new('RGB', (canvas_w, canvas_h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    margin_x = 30
    margin_y = 30
    
    # Header
    font_header = get_font(True, 32)
    draw.text((margin_x, margin_y), "Personajes", font=font_header, fill=(30, 30, 30))
    
    # Header underline
    draw.line([margin_x, margin_y + 45, canvas_w - margin_x, margin_y + 45], fill=(200, 200, 200), width=2)
    
    top_offset = margin_y + 65
    avail_h = canvas_h - margin_y - top_offset
    avail_w = canvas_w - (margin_x * 2)

    total_names = len(names)
    if total_names == 0:
        # En caso de no haber personajes
        draw.text((margin_x, top_offset), "N/A", font=get_font(False, 24), fill=(100, 100, 100))
        img.save(output_path)
        return

    # Lógica de distribución
    cols = 1
    font_size = 30
    row_height = 40
    
    if total_names <= 14:
        cols, font_size, row_height = 1, 30, 42
    elif total_names <= 30:
        cols, font_size, row_height = 2, 22, 32
    elif total_names <= 50:
        cols, font_size, row_height = 2, 19, 26
    else:
        # Secciones extremas (ej. 124 con 58 nombres)
        cols, font_size, row_height = 2, 19, 26
        max_rows = avail_h // row_height
        max_items = cols * max_rows
        if total_names > max_items:
            visible_count = max_items - 1
            remainder = total_names - visible_count
            names = names[:visible_count] + [f"... y {remainder} más"]

    text_font = get_font(False, font_size)
    italic_font = get_font(False, int(font_size * 0.9)) # fallback for '... y X mas'
    
    items_per_col = (len(names) + cols - 1) // cols
    col_width = avail_w / cols
    
    for i, name in enumerate(names):
        col = i // items_per_col
        row = i % items_per_col
        
        x = margin_x + col * col_width
        y = top_offset + row * row_height
        
        if name.startswith("..."):
            draw.text((x, y), name, font=get_font(True, font_size), fill=(80, 80, 80))
        else:
            # Usar viñeta y texto
            draw.text((x, y), "•", font=text_font, fill=(100, 100, 100))
            draw.text((x + 15, y), name, font=text_font, fill=(20, 20, 20))

    img.save(output_path)

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    data = parse_names(MD_FILE)
    count = 0
    
    # Generar secciones de la 1 a la 138 (DyC)
    for num in range(1, 139):
        names = data.get(('dyc', num), [])
        output_name = f"personajes_dyc_{num:03d}.png"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        render_names(num, names, output_path)
        count += 1
        
    # Extra: generar para las Declaraciones Oficiales
    # Sabemos que tenemos OD 1 y OD 2
    for num in [1, 2]:
        names = data.get(('declaración oficial', num), [])
        output_name = f"personajes_od_{num:03d}.png"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        render_names(num, names, output_path)
        count += 1
        
    print(f"Éxito. {count} imágenes generadas en {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
