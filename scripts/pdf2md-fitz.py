#!/usr/bin/env python3
"""PDF to Markdown using PyMuPDF (fitz) — font-size based heading detection."""
import sys
import time
import fitz  # PyMuPDF


def pdf_to_markdown(pdf_path: str, out_path: str):
    start = time.time()
    doc = fitz.open(pdf_path)
    print(f"Pages: {len(doc)}")

    # Pass 1: collect font size stats to detect headings
    font_sizes = {}
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:  # skip images
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    size = round(span["size"], 1)
                    text = span["text"].strip()
                    if text:
                        font_sizes[size] = font_sizes.get(size, 0) + len(text)

    # Determine body size (most common) and heading thresholds
    body_size = max(font_sizes, key=font_sizes.get)
    sorted_sizes = sorted(font_sizes.keys(), reverse=True)
    print(f"Body font size: {body_size}")
    print(f"Font sizes found: {sorted_sizes[:10]}")

    # Heading levels: sizes significantly larger than body
    heading_sizes = [s for s in sorted_sizes if s > body_size + 1.5]

    # Assign heading levels (largest = h1, next = h2, etc.)
    size_to_level = {}
    for i, s in enumerate(heading_sizes[:4]):  # max 4 heading levels
        size_to_level[s] = i + 1

    print(f"Heading sizes: {size_to_level}")

    # Pass 2: extract text with markdown formatting
    lines = []
    prev_block_bottom = 0

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue

            block_text_parts = []
            block_max_size = 0
            is_bold = False

            for line in block["lines"]:
                line_text = ""
                line_max_size = 0
                for span in line["spans"]:
                    text = span["text"]
                    if not text.strip():
                        line_text += text
                        continue
                    size = round(span["size"], 1)
                    line_max_size = max(line_max_size, size)
                    if "Bold" in span["font"] or "bold" in span["font"]:
                        is_bold = True
                    line_text += text

                line_text = line_text.strip()
                if line_text:
                    block_text_parts.append(line_text)
                    block_max_size = max(block_max_size, line_max_size)

            full_text = " ".join(block_text_parts).strip()
            if not full_text:
                continue

            # Skip page headers/footers (very short text at top/bottom)
            block_top = block["bbox"][1]
            block_bottom = block["bbox"][3]
            page_height = page.rect.height
            if len(full_text) < 20 and (block_top < 50 or block_bottom > page_height - 50):
                # Likely header/footer — skip
                continue

            # Determine if heading
            level = size_to_level.get(block_max_size, 0)
            if level == 0 and block_max_size > body_size + 0.5 and is_bold:
                # Bold + slightly larger = subheading
                level = min(len(size_to_level) + 1, 4)

            if level > 0:
                lines.append("")
                lines.append(f"{'#' * level} {full_text}")
                lines.append("")
            else:
                lines.append(full_text)
                lines.append("")  # paragraph break

    # Write output
    text = "\n".join(lines)
    # Clean up excessive blank lines
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    elapsed = time.time() - start
    line_count = text.count("\n")
    print(f"Output: {out_path}")
    print(f"Lines: {line_count}")
    print(f"Time: {elapsed:.1f}s")


if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/JFSDoctrinesofSalvationv1-3.pdf"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/fitz-out/doctrines_of_salvation.md"

    import os
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pdf_to_markdown(pdf_path, out_path)
