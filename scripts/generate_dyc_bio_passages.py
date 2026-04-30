from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAMELIST_PATH = ROOT / "prods" / "dyc_bios" / "namelist.md"
OUTPUT_PATH = ROOT / "prods" / "dyc_bios" / "namelist_with_passages.md"
SECTIONS_DIR = ROOT / "corpus" / "en" / "scriptures" / "dc" / "sections"
DECLARATIONS_DIR = ROOT / "corpus" / "en" / "scriptures" / "dc" / "official-declarations"
VERSE_RE = re.compile(r"^(\d+)\s+(.*)$")


SPECIAL_VARIANTS = {
    "Don C. Smith": ["Don Carlos Smith"],
    "Joseph F. Smith": ["Joseph Fielding Smith"],
    "Joseph Smith Jr.": ["Joseph Smith, Jun.", "Joseph Smith Jun.", "Joseph Smith Jr"],
    "Joseph Smith Sr.": ["Joseph Smith, Sen.", "Joseph Smith Sen.", "Joseph Smith Sr"],
    "Luke S. Johnson": ["Luke Johnson"],
    "Lyman E. Johnson": ["Lyman Johnson"],
    "Peter Whitmer Jr.": ["Peter Whitmer, Jun.", "Peter Whitmer Jun.", "Peter Whitmer Jr"],
    "Peter Whitmer Sr.": ["Peter Whitmer, Sen.", "Peter Whitmer Sen.", "Peter Whitmer Sr"],
    "William E. McLellin": ["William McLellin"],
}


def load_names(path: Path) -> list[str]:
    names = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue
        name = line[2:].strip()
        if name:
            names.append(name)
    return names


def build_variants(name: str) -> list[str]:
    variants = {name}
    variants.update(SPECIAL_VARIANTS.get(name, []))
    variants.add(name.replace(".", ""))

    for suffix, corpus_suffix in (("Jr.", "Jun."), ("Sr.", "Sen.")):
        needle = " %s" % suffix
        if name.endswith(needle):
            stem = name[: -len(needle)]
            variants.add("%s, %s" % (stem, corpus_suffix))
            variants.add("%s %s" % (stem, corpus_suffix))

    cleaned = []
    for variant in variants:
        value = variant.strip()
        if value:
            cleaned.append(value)
    return sorted(set(cleaned), key=lambda item: (-len(item), item))


def compile_patterns(names: list[str]) -> dict[str, list[re.Pattern[str]]]:
    compiled = {}
    for name in names:
        patterns = []
        for variant in build_variants(name):
            escaped = re.escape(variant)
            escaped = escaped.replace(r"\ ", r"(?:\s|\u00A0)+")
            patterns.append(re.compile(r"(?<![A-Za-z])%s(?![A-Za-z])" % escaped))
        compiled[name] = patterns
    return compiled


def normalize_verses(verses: set[int]) -> str:
    ordered = sorted(verses)
    if not ordered:
        return ""

    spans = []
    start = ordered[0]
    end = ordered[0]
    for verse in ordered[1:]:
        if verse == end + 1:
            end = verse
            continue
        spans.append((start, end))
        start = verse
        end = verse
    spans.append((start, end))

    rendered = []
    for start, end in spans:
        if start == end:
            rendered.append(str(start))
        else:
            rendered.append("%s-%s" % (start, end))
    return ", ".join(rendered)


def iter_docs(directory: Path, label_prefix: str):
    for text_path in sorted(directory.glob("*.txt"), key=lambda path: int(path.stem)):
        label = "%s %s" % (label_prefix, int(text_path.stem))
        meta_path = text_path.with_suffix(".meta.json")
        yield label, text_path, meta_path


def metadata_mentions(meta_path: Path, patterns: list[re.Pattern[str]]) -> bool:
    if not meta_path.exists():
        return False
    data = json.loads(meta_path.read_text(encoding="utf-8"))
    haystacks = []
    for key in ("summary", "meta_description", "study_intro"):
        value = data.get(key)
        if isinstance(value, str):
            haystacks.append(value)
    if not haystacks:
        return False
    text = "\n".join(haystacks)
    return any(pattern.search(text) for pattern in patterns)


def collect_mentions(names: list[str]) -> dict[str, list[str]]:
    patterns_by_name = compile_patterns(names)
    body_hits = defaultdict(lambda: defaultdict(set))
    header_hits = defaultdict(set)

    for label, text_path, meta_path in list(iter_docs(SECTIONS_DIR, "DyC")) + list(
        iter_docs(DECLARATIONS_DIR, "Declaración Oficial")
    ):
        text = text_path.read_text(encoding="utf-8")
        for raw_line in text.splitlines():
            match = VERSE_RE.match(raw_line.strip())
            if not match:
                continue
            verse = int(match.group(1))
            verse_text = match.group(2)
            for name, patterns in patterns_by_name.items():
                if any(pattern.search(verse_text) for pattern in patterns):
                    body_hits[name][label].add(verse)

        for name, patterns in patterns_by_name.items():
            if label not in body_hits[name] and metadata_mentions(meta_path, patterns):
                header_hits[name].add(label)

    rendered = {}
    for name in names:
        refs = []
        for label in sorted(body_hits[name], key=sort_key):
            refs.append("%s:%s" % (label, normalize_verses(body_hits[name][label])))
        for label in sorted(header_hits[name], key=sort_key):
            refs.append("%s (encabezado)" % label)
        rendered[name] = refs
    return rendered


def sort_key(label: str) -> tuple[int, int]:
    if label.startswith("Declaración Oficial"):
        return (1, int(label.rsplit(" ", 1)[1]))
    return (0, int(label.rsplit(" ", 1)[1]))


def render_markdown(names: list[str], mentions: dict[str, list[str]]) -> str:
    lines = [
        "# Nombres En DyC Con Pasajes",
        "",
        "Base derivada de `prods/dyc_bios/namelist.md`. Se escanearon las 138 secciones y las 2 Declaraciones Oficiales en el corpus inglés de DyC para localizar menciones por nombre.",
        "",
    ]
    for name in names:
        lines.append("## %s" % name)
        refs = mentions.get(name, [])
        if refs:
            for ref in refs:
                lines.append("- %s" % ref)
        else:
            lines.append("- Sin referencias localizadas en el texto o encabezados escaneados")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    names = load_names(NAMELIST_PATH)
    mentions = collect_mentions(names)
    OUTPUT_PATH.write_text(render_markdown(names, mentions), encoding="utf-8")
    total_refs = sum(len(values) for values in mentions.values())
    print(
        json.dumps(
            {
                "names": len(names),
                "output": str(OUTPUT_PATH.relative_to(ROOT)).replace("\\", "/"),
                "references": total_refs,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()