import os
import re

def generate_html(title, pericopes, output_path):
    # pericopes is list of (start, end, title)
    
    rows = []
    for start, end, p_title in pericopes:
        verse_str = f"{start}-{end}" if start != end else f"{start}"
        rows.append((p_title, verse_str))
    
    # Split rows into columns of max 12
    cols = [rows[i:i + 12] for i in range(0, len(rows), 12)]
    
    col_html = ""
    for col in cols:
        table_rows = ""
        for p_title, v_str in col:
            table_rows += f"""
            <tr>
                <td class="pericope-title">{p_title}</td>
                <td class="verses">{v_str}</td>
            </tr>
            """
        
        col_html += f"""
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Título</th>
                        <th>Versículos</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: white;
                color: #333;
                margin: 0;
                padding: 40px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            h1 {{
                font-size: 24px;
                margin-bottom: 30px;
                color: #222;
            }}
            .main-container {{
                display: flex;
                gap: 40px;
                align-items: flex-start;
            }}
            .table-container {{
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
            table {{
                border-collapse: collapse;
                width: auto;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: bold;
                color: #000;
                border-bottom: 2px solid #ddd;
            }}
            .pericope-title {{
                white-space: nowrap;
                min-width: 400px;
                font-size: 14px;
            }}
            .verses {{
                text-align: right;
                font-weight: 500;
                min-width: 80px;
                font-size: 14px;
                color: #555;
            }}
            tr:last-child td {{
                border-bottom: none;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <div class="main-container">
            {col_html}
        </div>
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def parse_md(filepath):
    pericopes = []
    section_title = ""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('# '):
                section_title = line[2:].strip()
            # Match table rows
            m = re.search(r'\| (.*?) \| (\d+)(?:-(\d+))? \|', line)
            if m:
                p_title = m.group(1).strip()
                if p_title.lower() == "titulo": continue
                v_start = int(m.group(2))
                v_end = int(m.group(3)) if m.group(3) else v_start
                pericopes.append((v_start, v_end, p_title))
    return section_title, pericopes

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python render_pericopas.py input.md output.html")
    else:
        title, data = parse_md(sys.argv[1])
        generate_html(title, data, sys.argv[2])
