import os
import re
from PIL import Image, ImageDraw, ImageFont

PERICOPAS_DIR = r"C:\own\alejandria\prods\bookdc\pericopas"
OUTPUT_DIR = r"C:\own\alejandria\prods\bookdc\pericopas_png"

def render_pericopes_to_png(title_text, pericopes, output_path):
    # Canvas Specs (Fixed Landscape)
    canvas_w = 1400
    canvas_h = 800
    
    img = Image.new('RGB', (canvas_w, canvas_h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Font library
    font_path = "C:\\Windows\\Fonts\\segoeui.ttf"
    font_path_bold = "C:\\Windows\\Fonts\\segoeuib.ttf"
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        font_path_bold = "C:\\Windows\\Fonts\\arialbd.ttf"

    def get_font(bold=False, size=18):
        try:
            return ImageFont.truetype(font_path_bold if bold else font_path, size)
        except:
            return ImageFont.load_default()

    font_title = get_font(True, 32)
    font_header = get_font(True, 20)
    
    # Layout Config
    margin_x = 45 # Reduced from 60
    margin_y = 50
    gutter = 50 
    row_height = 42
    header_height = 52
    
    draw.text((margin_x, margin_y), title_text, font=font_title, fill=(0, 0, 0))
    top_offset = margin_y + 90
    
    # Logic: How many rows can fit in one column?
    # 800 (h) - 50 (margin) - 90 (title area) - 50 (header) - 50 (footer margin) = 560px
    # 560 / 42 = 13.3 rows. Let's push to 15 rows with slightly tighter spacing if needed?
    # Actually, 14 rows at 42px = 588px.
    # 90 + 52 + 588 + 50 = 780px. Fits in 800.
    # So max_per_col = 14.
    max_per_col = 14
    
    cols_data = [pericopes[i:i + max_per_col] for i in range(0, len(pericopes), max_per_col)]
    num_cols = len(cols_data)
    
    available_w = canvas_w - (margin_x * 2) - (gutter * (num_cols - 1))
    table_width = available_w / num_cols
    col2_width = 110
    col1_width = table_width - col2_width
    
    for c_idx, col_rows in enumerate(cols_data):
        left_x = margin_x + c_idx * (table_width + gutter)
        
        # Header
        draw.rectangle([left_x, top_offset, left_x + table_width, top_offset + header_height], fill=(245, 245, 245))
        draw.line([left_x, top_offset, left_x + table_width, top_offset], fill=(200, 200, 200), width=1)
        draw.line([left_x, top_offset + header_height, left_x + table_width, top_offset + header_height], fill=(150, 150, 150), width=2)
        
        draw.text((left_x + 15, top_offset + 12), "Título", font=font_header, fill=(0, 0, 0))
        draw.text((left_x + col1_width + 10, top_offset + 12), "Versículos", font=font_header, fill=(0, 0, 0))
        
        for r_idx, (start, end, p_title) in enumerate(col_rows):
            y = top_offset + header_height + r_idx * row_height
            
            draw.line([left_x, y + row_height, left_x + table_width, y + row_height], fill=(235, 235, 235), width=1)
            
            # Shrink to fit logic for title
            current_font_size = 18
            text_font = get_font(False, current_font_size)
            
            # Use textbbox to measure width (Pillow 10+)
            def get_text_width(text, font):
                bbox = draw.textbbox((0, 0), text, font=font)
                return bbox[2] - bbox[0]

            while get_text_width(p_title, text_font) > (col1_width - 25) and current_font_size > 12:
                current_font_size -= 1
                text_font = get_font(False, current_font_size)
            
            # Centering vertically in the row
            draw.text((left_x + 15, y + 10 + (18 - current_font_size)//2), p_title, font=text_font, fill=(20, 20, 20))
            
            # Verses (Fixed font 18)
            verse_str = f"{start}-{end}" if start != end else f"{start}"
            draw.text((left_x + col1_width + 10, y + 10), verse_str, font=get_font(False, 18), fill=(80, 80, 80))
            
        draw.line([left_x + col1_width, top_offset, left_x + col1_width, top_offset + header_height + len(col_rows) * row_height], fill=(220, 220, 220), width=1)
        draw.rectangle([left_x, top_offset, left_x + table_width, top_offset + header_height + len(col_rows) * row_height], outline=(150, 150, 150), width=1)

    img.save(output_path)

def parse_md(filepath):
    pericopes = []
    section_title = ""
    if not os.path.exists(filepath): return "", []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('# '):
                section_title = line[2:].strip()
            m = re.search(r'\| (.*?) \| (\d+)(?:-(\d+))? \|', line)
            if m:
                p_title = m.group(1).strip()
                if p_title.lower() == "titulo" or p_title.startswith('---'): continue
                v_start = int(m.group(2))
                v_end = int(m.group(3)) if m.group(3) else v_start
                pericopes.append((v_start, v_end, p_title))
    return section_title, pericopes

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    md_files = [f for f in os.listdir(PERICOPAS_DIR) if f.startswith("Esquema de DyC") and f.endswith(".md")]
    def get_section_num(filename):
        m = re.search(r'DyC (\d+)', filename)
        return int(m.group(1)) if m else 0
    md_files.sort(key=get_section_num)
    count = 0
    for filename in md_files:
        section_num = get_section_num(filename)
        if section_num == 0: continue
        input_path = os.path.join(PERICOPAS_DIR, filename)
        output_name = f"esquema_dyc_{section_num:03d}.png"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        title, data = parse_md(input_path)
        if data:
            render_pericopes_to_png(title, data, output_path)
            count += 1
            if count % 20 == 0: print(f"Rendered {count} / {len(md_files)}...")
    print(f"Finished! {count} images regenerated in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
