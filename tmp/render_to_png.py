import os
import re
from PIL import Image, ImageDraw, ImageFont

def render_pericopes_to_png(title_text, pericopes, output_path):
    # Font settings
    try:
        # Try to find a sans-serif font on Windows
        font_path = "C:\\Windows\\Fonts\\segoeui.ttf"
        font_path_bold = "C:\\Windows\\Fonts\\segoeuib.ttf"
        if not os.path.exists(font_path):
            font_path = "C:\\Windows\\Fonts\\arial.ttf"
            font_path_bold = "C:\\Windows\\Fonts\\arialbd.ttf"
            
        font_title = ImageFont.truetype(font_path_bold, 28)
        font_header = ImageFont.truetype(font_path_bold, 18)
        font_text = ImageFont.truetype(font_path, 16)
    except:
        # Fallback to default
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # Table specs
    col1_width = 550
    col2_width = 100
    row_height = 35
    header_height = 45
    margin = 40
    gutter = 60 # Space between tables
    
    # Split rows into max 12
    cols_data = [pericopes[i:i + 12] for i in range(0, len(pericopes), 12)]
    num_cols = len(cols_data)
    
    table_width = col1_width + col2_width
    total_width = margin * 2 + table_width * num_cols + gutter * (num_cols - 1)
    
    # Height is fixed by the max number of rows (12) + header + title
    max_rows = 12
    canvas_height = margin * 2 + 100 + header_height + max_rows * row_height
    
    # Create image
    img = Image.new('RGB', (int(total_width), int(canvas_height)), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw Title
    draw.text((margin, margin), title_text, font=font_title, fill=(0, 0, 0))
    
    top_offset = margin + 80
    
    for c_idx, col_rows in enumerate(cols_data):
        left_x = margin + c_idx * (table_width + gutter)
        
        # Draw Header Background
        draw.rectangle([left_x, top_offset, left_x + table_width, top_offset + header_height], fill=(245, 245, 245))
        draw.line([left_x, top_offset, left_x + table_width, top_offset], fill=(200, 200, 200), width=1)
        draw.line([left_x, top_offset + header_height, left_x + table_width, top_offset + header_height], fill=(180, 180, 180), width=2)

        # Header Text
        draw.text((left_x + 15, top_offset + 12), "Título", font=font_header, fill=(0, 0, 0))
        draw.text((left_x + col1_width + 10, top_offset + 12), "Versículos", font=font_header, fill=(0, 0, 0))
        
        # Draw Rows
        for r_idx, (start, end, p_title) in enumerate(col_rows):
            y = top_offset + header_height + r_idx * row_height
            
            # Row line
            if r_idx < len(col_rows) - 1:
                draw.line([left_x, y + row_height, left_x + table_width, y + row_height], fill=(230, 230, 230), width=1)
            
            # Pericope title (truncated if too long, but user wants no wrap, so we just clip or use large fixed width)
            # We'll just draw it.
            draw.text((left_x + 15, y + 8), p_title, font=font_text, fill=(30, 30, 30))
            
            # Verses
            verse_str = f"{start}-{end}" if start != end else f"{start}"
            draw.text((left_x + col1_width + 10, y + 8), verse_str, font=font_text, fill=(80, 80, 80))
            
        # Draw outer border for table
        draw.rectangle([left_x, top_offset, left_x + table_width, top_offset + header_height + len(col_rows) * row_height], outline=(200, 200, 200), width=1)

    img.save(output_path)

def parse_md(filepath):
    pericopes = []
    section_title = ""
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

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python render_to_png.py input.md output.png")
    else:
        title, data = parse_md(sys.argv[1])
        render_pericopes_to_png(title, data, sys.argv[2])
