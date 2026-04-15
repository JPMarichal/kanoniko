#!/usr/bin/env python3
"""Clean and split Doctrines of Salvation into corpus-ready chapter files."""
import re
import os

RAW = "pdf/doctrines_of_salvation_raw.md"
CORPUS_BASE = "corpus/en/books/doctrines-of-salvation"

def clean_text(text: str) -> str:
    """Clean up common PyMuPDF extraction artifacts."""
    # Fix footnote references: "39. 8" -> "39.8", "1.1" stays
    text = re.sub(r'(\d+)\.\s+(\d+)', r'\1.\2', text)

    # Fix line breaks within paragraphs (line ending without period/colon/etc)
    # A line that doesn't end with sentence-ending punctuation followed by
    # a line that starts with lowercase = broken paragraph
    text = re.sub(r'(?<![.!?:;"\'])\n(?=[a-z])', ' ', text)

    # Clean up multiple spaces
    text = re.sub(r'  +', ' ', text)

    # Clean up excessive blank lines
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')

    return text.strip()


def merge_split_headings(lines):
    """Merge chapter headings that were split across two lines.

    Pattern: '### CHAPTER N' followed by '### TITLE' -> '### CHAPTER N — TITLE'
    """
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r'^### CHAPTER \d+$', line.strip()):
            # Look ahead for the title on next non-empty line
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].startswith('### '):
                title = lines[j].lstrip('# ').strip()
                result.append(f"{line.strip()} — {title}")
                i = j + 1
                continue
        result.append(line)
        i += 1
    return result


def split_into_volumes(text: str) -> dict:
    """Split text into volumes at '## Volume N' markers."""
    parts = re.split(r'\n## Volume (I+)\n', text)
    # parts[0] = title/preamble, then alternating: volume_num, content

    volumes = {}
    for i in range(1, len(parts), 2):
        vol_num = parts[i]
        vol_content = parts[i + 1]
        volumes[vol_num] = vol_content

    return volumes


def split_into_chapters(vol_text: str) -> list:
    """Split volume text into (chapter_heading, chapter_content) pairs."""
    # Split on chapter headings
    parts = re.split(r'\n(### CHAPTER \d+.*)\n', vol_text)

    chapters = []
    preface = parts[0].strip()
    if preface:
        chapters.append(("preface", preface))

    for i in range(1, len(parts), 2):
        heading = parts[i].strip().lstrip('# ')
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""

        # Remove footnotes section at end
        fn_match = re.search(r'\n### Footnotes to Volume', content)
        if fn_match:
            footnotes = content[fn_match.start():]
            content = content[:fn_match.start()].strip()
            # We'll save footnotes separately
            chapters.append((heading, content))
            chapters.append(("footnotes", footnotes.strip()))
        else:
            chapters.append((heading, content))

    return chapters


def chapter_filename(heading: str) -> str:
    """Convert chapter heading to filename."""
    if heading == "preface":
        return "00-preface.md"
    if heading == "footnotes":
        return "99-footnotes.md"

    # Extract chapter number and title
    m = re.match(r'CHAPTER (\d+)\s*[—-]?\s*(.*)', heading)
    if m:
        num = int(m.group(1))
        title = m.group(2).strip()
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        if slug:
            return f"{num:02d}-{slug}.md"
        return f"{num:02d}.md"

    slug = re.sub(r'[^a-z0-9]+', '-', heading.lower()).strip('-')
    return f"{slug}.md"


def vol_dir(vol_num: str) -> str:
    """Volume number to directory name."""
    mapping = {'I': 'vol1', 'II': 'vol2', 'III': 'vol3'}
    return mapping.get(vol_num, f'vol-{vol_num}')


def main():
    with open(RAW, 'r', encoding='utf-8') as f:
        raw = f.read()

    print(f"Raw input: {len(raw)} chars, {raw.count(chr(10))} lines")

    # Clean
    text = clean_text(raw)
    lines = text.split('\n')
    lines = merge_split_headings(lines)
    text = '\n'.join(lines)

    print(f"After cleaning: {len(text)} chars")

    # Split into volumes
    volumes = split_into_volumes(text)
    print(f"Volumes found: {list(volumes.keys())}")

    total_files = 0
    for vol_num, vol_text in volumes.items():
        chapters = split_into_chapters(vol_text)
        vdir = os.path.join(CORPUS_BASE, vol_dir(vol_num))
        os.makedirs(vdir, exist_ok=True)

        print(f"\nVolume {vol_num}: {len(chapters)} files")
        for heading, content in chapters:
            fname = chapter_filename(heading)
            fpath = os.path.join(vdir, fname)

            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content + '\n')

            line_count = content.count('\n') + 1
            print(f"  {fname}: {line_count} lines")
            total_files += 1

    print(f"\nTotal: {total_files} files written to {CORPUS_BASE}/")


if __name__ == '__main__':
    main()
