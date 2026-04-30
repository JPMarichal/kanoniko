from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAMELIST_PATH = ROOT / "prods" / "dyc_bios" / "namelist.md"
OUTPUT_PATH = ROOT / "prods" / "dyc_bios" / "matriz_de_fuentes.md"

EN_BIO_DIR = ROOT / "corpus" / "en" / "biographies"
ES_BIO_DIR = ROOT / "corpus" / "es" / "biographies"
GA_DIR = EN_BIO_DIR / "general-authorities"

DIRECT_MATCH_EXCLUDE_PREFIXES = (
    "lds-biographical-encyclopedia-vol-",
)


SPECIAL_VARIANTS = {
    "Don C. Smith": ["Don Carlos Smith"],
    "Joseph F. Smith": ["Joseph Fielding Smith"],
    "Joseph Smith Jr.": ["Joseph Smith"],
    "Joseph Smith Sr.": ["Joseph Smith"],
    "Luke S. Johnson": ["Luke Johnson"],
    "Lyman E. Johnson": ["Lyman Johnson"],
    "Peter Whitmer Jr.": ["Peter Whitmer"],
    "Peter Whitmer Sr.": ["Peter Whitmer"],
    "William E. McLellin": ["William McLellin"],
}

DIRECT_SOURCE_OVERRIDES = {
    "Hyrum Smith": "Hyrum Smith, Patriarch",
    "Joseph Smith Jr.": "Joseph Smith, the Prophet, the Man; GAPages",
    "Joseph Smith Sr.": "Father of the Prophet, Stories and Insights from the Life of Joseph Smith, Sr.",
}


def load_names(path: Path) -> list[str]:
    return [line[2:].strip() for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("- ")]


def normalize_text(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9\s]", " ", value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
    return cleaned


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", normalize_text(value)).strip("-")


def tokens(value: str) -> list[str]:
    return [part for part in slugify(value).split("-") if part]


def build_variants(name: str) -> list[list[str]]:
    values = {name}
    values.update(SPECIAL_VARIANTS.get(name, []))

    base = normalize_text(name)
    base_no_suffix = re.sub(r"\b(jr|sr)\b", " ", base)
    base_no_initials = re.sub(r"\b[a-z0-9]\b", " ", base)
    base_compact = re.sub(r"\s+", " ", base_no_suffix).strip()
    base_compact_no_initials = re.sub(r"\s+", " ", re.sub(r"\b[a-z0-9]\b", " ", base_compact)).strip()

    values.update(filter(None, [base, base_no_suffix, base_no_initials, base_compact, base_compact_no_initials]))

    rendered = []
    seen = set()
    for value in values:
        item_tokens = tokens(value)
        if len(item_tokens) < 2:
            continue
        key = tuple(item_tokens)
        if key in seen:
            continue
        seen.add(key)
        rendered.append(item_tokens)
    return sorted(rendered, key=lambda item: (-len(item), item))


def contains_sequence(haystack: list[str], needle: list[str]) -> bool:
    if len(needle) > len(haystack):
        return False
    for index in range(len(haystack) - len(needle) + 1):
        if haystack[index : index + len(needle)] == needle:
            return True
    return False


def contains_ordered_tokens(haystack: list[str], needle: list[str]) -> bool:
    if len(needle) > len(haystack):
        return False
    position = 0
    for token in haystack:
        if token == needle[position]:
            position += 1
            if position == len(needle):
                return True
    return False


def first_meta_json(directory: Path) -> Path | None:
    files = sorted(directory.glob("*.meta.json"))
    return files[0] if files else None


def iter_meta_json(directory: Path) -> list[Path]:
    return sorted(directory.glob("*.meta.json"))


def read_title(meta_path: Path | None, fallback: str) -> str:
    if meta_path is None:
        return fallback
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return str(data.get("book") or data.get("title") or fallback).strip()


def biography_directories() -> list[Path]:
    dirs = []
    for base in (EN_BIO_DIR, ES_BIO_DIR):
        for item in sorted(base.iterdir()):
            if not item.is_dir():
                continue
            if item.name == "general-authorities":
                continue
            dirs.append(item)
    return dirs


def build_directory_index(directories: list[Path]) -> list[dict[str, object]]:
    indexed = []
    for directory in directories:
        if directory.name.startswith(DIRECT_MATCH_EXCLUDE_PREFIXES):
            continue

        title = read_title(first_meta_json(directory), directory.name.replace("-", " "))
        self_haystacks = [directory.name.split("-"), tokens(title)]
        chapter_haystacks = []

        for meta_path in iter_meta_json(directory):
            try:
                data = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            title_value = data.get("title")
            if isinstance(title_value, str) and title_value.strip():
                chapter_haystacks.append(tokens(title_value))

        indexed.append({"title": title, "self_haystacks": self_haystacks, "chapter_haystacks": chapter_haystacks})
    return indexed


def direct_bio_hits(name: str, directory_index: list[dict[str, object]]) -> list[str]:
    if name in DIRECT_SOURCE_OVERRIDES:
        return [DIRECT_SOURCE_OVERRIDES[name]]

    variants = build_variants(name)
    direct_hits = []
    fallback_hits = []
    for entry in directory_index:
        self_haystacks = entry["self_haystacks"]
        chapter_haystacks = entry["chapter_haystacks"]
        if any(
            contains_sequence(haystack, variant)
            for haystack in self_haystacks
            for variant in variants
        ):
            direct_hits.append(str(entry["title"]))
            continue
        if any(
            contains_sequence(haystack, variant) or contains_ordered_tokens(haystack, variant)
            for haystack in chapter_haystacks
            for variant in variants
        ):
            fallback_hits.append(str(entry["title"]))

    chosen = direct_hits or fallback_hits
    return sorted(dict.fromkeys(chosen))


def ga_hit(name: str) -> bool:
    variants = build_variants(name)
    for meta_path in sorted(GA_DIR.glob("*.meta.json")):
        haystack = meta_path.stem.split("-")
        if any(contains_sequence(haystack, variant) for variant in variants):
            return True
    return False


def classify(name: str, direct_hits: list[str], has_ga: bool) -> tuple[str, str, str, str]:
    if direct_hits:
        return (
            "; ".join(direct_hits[:2]),
            "Revelaciones en contexto; Santos",
            "Doctrina y Convenios - Manual del alumno; namelist_with_passages.md; GEE",
            "biografia_dedicada",
        )
    if has_ga:
        return (
            "LDS Biographical Encyclopedia; GAPages",
            "Revelaciones en contexto; Santos",
            "Doctrina y Convenios - Manual del alumno; namelist_with_passages.md; GEE",
            "ficha_ga_probable",
        )
    return (
        "LDS Biographical Encyclopedia",
        "Revelaciones en contexto; Santos; Church History and Modern Revelation",
        "Doctrina y Convenios - Manual del alumno; namelist_with_passages.md; GEE",
        "ruta_generica",
    )


def render_markdown(names: list[str]) -> str:
    directory_index = build_directory_index(biography_directories())
    lines = [
        "# Matriz De Fuentes Para Personajes De DyC",
        "",
        "Matriz operativa derivada de `prods/dyc_bios/namelist.md` y de las familias de fuentes confirmadas en `prods/dyc_bios/fuentes.md`.",
        "",
        "Lectura de columnas:",
        "",
        "- `fuente_puntual`: la mejor fuente sugerida para arrancar el perfil de esa persona.",
        "- `capa_contextual`: fuentes narrativas o de trasfondo histórico que conviene cruzar después.",
        "- `capa_de_apoyo`: pasajes, manuales y ayudas de normalización.",
        "- `estado`: indica si hay biografía dedicada detectada, ficha probable en GA o sólo ruta genérica.",
        "",
        "| nombre | fuente_puntual | capa_contextual | capa_de_apoyo | estado |",
        "|---|---|---|---|---|",
    ]

    for name in names:
        direct_hits = direct_bio_hits(name, directory_index)
        has_ga = ga_hit(name)
        puntual, contextual, apoyo, status = classify(name, direct_hits, has_ga)
        lines.append(f"| {name} | {puntual} | {contextual} | {apoyo} | {status} |")

    lines.extend(
        [
            "",
            "## Leyenda De Estado",
            "",
            "- `biografia_dedicada`: el corpus ya contiene una obra monografica o autobiografica que probablemente cubre directamente a la persona.",
            "- `ficha_ga_probable`: no se detecto monografia clara, pero si una ficha probable en `general-authorities/`.",
            "- `ruta_generica`: no se detecto biografia puntual por nombre; conviene arrancar por enciclopedias, contexto de la seccion y pasajes.",
            "",
            "## Notas",
            "",
            "- La matriz usa coincidencia por nombre sobre slugs y variantes basicas; no sustituye verificacion humana en casos ambiguos.",
            "- Para todos los nombres, el anclaje canonico sigue siendo `prods/dyc_bios/namelist_with_passages.md`.",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    names = load_names(NAMELIST_PATH)
    OUTPUT_PATH.write_text(render_markdown(names), encoding="utf-8")
    print(json.dumps({"names": len(names), "output": str(OUTPUT_PATH.relative_to(ROOT)).replace("\\", "/")}, ensure_ascii=False))


if __name__ == "__main__":
    main()