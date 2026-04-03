"""Document parsers for supported formats: md, txt, html, json."""

from __future__ import annotations

import json
from pathlib import Path

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt


def parse_file(path: Path) -> str:
    """Parse a file and return plain text content.

    Dispatches to the appropriate parser based on file extension.
    """
    suffix = path.suffix.lower()
    raw = path.read_text(encoding="utf-8", errors="replace")

    parsers = {
        ".md": _parse_markdown,
        ".txt": _parse_text,
        ".html": _parse_html,
        ".htm": _parse_html,
        ".json": _parse_json,
    }

    parser = parsers.get(suffix)
    if parser is None:
        raise ValueError(f"Unsupported file extension: {suffix}")

    return parser(raw)


def _parse_markdown(raw: str) -> str:
    md = MarkdownIt()
    html = md.render(raw)
    return _strip_html(html)


def _parse_text(raw: str) -> str:
    return raw


def sanitize_html(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove non-content elements from HTML before text extraction.

    This is the single point of control for HTML sanitization.  Every path
    that converts HTML to indexable text (parsers, pandoc scripts, downloaders)
    MUST call this function first.  Prevents NER pollution from metadata
    (speaker+title compounds) and footnotes (name+calling concatenations).

    Removes: head, style, script, .header, .extraction-info, .notes, footer.
    """
    for selector in (
        "head", "style", "script",       # page chrome
        ".header", ".extraction-info",    # corpus HTML metadata divs
        ".notes", "footer",              # footnotes — already in .meta.json
        ".study-note-ref", "sup.marker",  # inline note markers
    ):
        for tag in soup.select(selector):
            tag.decompose()
    return soup


def _parse_html(raw: str) -> str:
    soup = BeautifulSoup(raw, "html.parser")
    sanitize_html(soup)
    return soup.get_text(separator="\n", strip=True)


def _parse_json(raw: str) -> str:
    data = json.loads(raw)
    return _extract_json_text(data)


def _strip_html(html: str) -> str:
    """Strip HTML tags for non-HTML source formats (e.g. markdown rendered to HTML)."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def _extract_json_text(data: object, depth: int = 0) -> str:
    """Recursively extract string values from a JSON structure."""
    if depth > 20:
        return ""

    if isinstance(data, str):
        return data
    if isinstance(data, list):
        parts = [_extract_json_text(item, depth + 1) for item in data]
        return "\n".join(p for p in parts if p)
    if isinstance(data, dict):
        parts = []
        for value in data.values():
            text = _extract_json_text(value, depth + 1)
            if text:
                parts.append(text)
        return "\n".join(parts)
    return ""
