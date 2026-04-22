"""
Authors inventory for epub/!Ready.

Read-only. Produces:
  epub/_authors.csv   one row per (creator_raw, publisher_raw) unique pair
  epub/_authors.md    normalized groups + flag cases that need author/publisher decision

Special focus: "La Iglesia de Jesucristo..." variants — detect when it should be
author, publisher, or both.
"""
from __future__ import annotations
import csv
import re
import unicodedata
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN_CSV = ROOT / "epub" / "_inventory.csv"
OUT_CSV = ROOT / "epub" / "_authors.csv"
OUT_MD = ROOT / "epub" / "_authors.md"

CHURCH_PATTERNS = [
    r"iglesia de jesucristo",
    r"church of jesus christ",
    r"lds church",
    r"the church of jesus christ of latter",
    r"santos de los .ltimos d.as",
    r"latter-?day saints",
]
CHURCH_RE = re.compile("|".join(CHURCH_PATTERNS), re.IGNORECASE)

PLACEHOLDER_UNKNOWN = {
    "desconocido", "unknown", "no specific author", "anonymous",
    "anonimo", "anónimo", "n/a", "",
}
PLACEHOLDER_MULTI = {"various", "various authors", "varios", "varios autores"}
PLACEHOLDER_AUTHORS = PLACEHOLDER_UNKNOWN | PLACEHOLDER_MULTI


def normalize_initials(name: str) -> str:
    """Insert dot after single-letter initials: 'James E Talmage' -> 'James E. Talmage'."""
    if not name:
        return name
    parts = name.split()
    out = []
    for p in parts:
        # Single uppercase letter, or letter+period missing — add dot
        if re.fullmatch(r"[A-ZÁÉÍÓÚÑ]", p):
            out.append(p + ".")
        else:
            out.append(p)
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def norm_key(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"\s+", " ", s).strip().lower()
    # collapse punctuation except hyphens/dots for initials
    s = re.sub(r"[^\w\s\.-]", "", s)
    return s


def canonical_creator(raw: str) -> str:
    """Collapse variants to a canonical display name.

    Rules:
    - Church variants -> "IJCSUD" (cross-idioma)
    - Unknown/Desconocido/No specific -> "(unknown)"
    - Various / Various authors / Varios -> "Various"  (multi-author collection)
    - Drop "(1)" suffixes from calibre dedup
    - Insert dot after bare initials: "James E Talmage" -> "James E. Talmage"
    """
    if not raw:
        return "(unknown)"
    r = raw.strip()
    r = re.sub(r"\s*\(\d+\)\s*$", "", r)
    rl = norm_key(r)
    if CHURCH_RE.search(rl):
        return "IJCSUD"
    if rl in PLACEHOLDER_UNKNOWN:
        return "(unknown)"
    if rl in PLACEHOLDER_MULTI:
        return "Various"
    return normalize_initials(r)


def main() -> int:
    if not IN_CSV.exists():
        print(f"Run scripts/epub_inventory.py first — missing {IN_CSV}")
        return 1

    rows = list(csv.DictReader(IN_CSV.open(encoding="utf-8")))

    # Pair (creator, publisher) counts
    pair_counts: Counter = Counter()
    creator_to_publishers: dict[str, Counter] = defaultdict(Counter)
    publisher_to_creators: dict[str, Counter] = defaultdict(Counter)
    canonical_groups: dict[str, list[str]] = defaultdict(list)  # canonical -> raw variants
    canonical_files: dict[str, int] = Counter()
    creator_langs: dict[str, Counter] = defaultdict(Counter)

    for r in rows:
        raw_creator = r["creator"].strip()
        raw_publisher = r["publisher"].strip()
        canonical = canonical_creator(raw_creator)
        canonical_groups[canonical].append(raw_creator)
        canonical_files[canonical] += 1
        pair_counts[(raw_creator, raw_publisher)] += 1
        creator_to_publishers[canonical][raw_publisher or "(sin publisher)"] += 1
        if raw_publisher:
            publisher_to_creators[raw_publisher][canonical] += 1
        creator_langs[canonical][r["lang"]] += 1

    # CSV: one row per unique pair
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["creator_raw", "publisher_raw", "canonical_creator", "n_files", "is_church_variant", "is_placeholder"])
        for (cr, pb), n in sorted(pair_counts.items(), key=lambda x: -x[1]):
            can = canonical_creator(cr)
            is_church = bool(CHURCH_RE.search(norm_key(cr))) or bool(CHURCH_RE.search(norm_key(pb)))
            is_ph = norm_key(cr) in PLACEHOLDER_AUTHORS
            w.writerow([cr, pb, can, n, is_church, is_ph])

    # Markdown report
    lines = []
    lines.append(f"# Authors inventory — {len(rows)} archivos, {len(canonical_groups)} autores canónicos\n")

    # --- Church cases (author/publisher decision) ---
    lines.append("## 1. Casos IJCSUD — normalización autor / publisher\n")
    lines.append("Regla: cualquier variante ('La Iglesia de Jesucristo...', 'Church of Jesus Christ...', etc.) → `author: \"IJCSUD\"` y `publisher: \"IJCSUD\"` (heredar). Aplica a ambos idiomas por igual.\n")
    lines.append("| creator_raw | publisher_raw | n |")
    lines.append("|---|---|---:|")
    church_pairs = []
    for (cr, pb), n in pair_counts.items():
        cr_is_church = bool(CHURCH_RE.search(norm_key(cr)))
        pb_is_church = bool(CHURCH_RE.search(norm_key(pb)))
        if cr_is_church or pb_is_church:
            church_pairs.append((cr, pb, n, cr_is_church, pb_is_church))
    church_pairs.sort(key=lambda x: -x[2])
    for cr, pb, n, crc, pbc in church_pairs[:40]:
        lines.append(f"| {cr[:50]} | {pb[:40] or '(vacío)'} | {n} |")
    lines.append("")
    if len(church_pairs) > 40:
        lines.append(f"_({len(church_pairs)-40} casos adicionales en CSV)_\n")

    # --- Placeholder authors ---
    lines.append("## 2. Autores placeholder (requieren investigación)\n")
    lines.append("| canonical | n | ejemplos de publisher |")
    lines.append("|---|---:|---|")
    for can in sorted(canonical_groups.keys()):
        if can.startswith("(placeholder"):
            pubs = creator_to_publishers[can].most_common(3)
            pub_str = ", ".join(f"{p or '(vacío)'} ({c})" for p, c in pubs)
            lines.append(f"| {can} | {canonical_files[can]} | {pub_str} |")
    lines.append("")

    # --- Top 50 canonical authors ---
    lines.append("## 3. Top 50 autores canónicos\n")
    lines.append("| # | autor canónico | n | lang | variantes raw |")
    lines.append("|---:|---|---:|---|---|")
    top = sorted(canonical_groups.items(), key=lambda x: -canonical_files[x[0]])[:50]
    for i, (can, variants) in enumerate(top, 1):
        uniq_variants = sorted(set(v for v in variants if v and v.strip() != can))
        var_str = "; ".join(uniq_variants[:5])
        if len(uniq_variants) > 5:
            var_str += f" (+{len(uniq_variants)-5})"
        lang_str = " ".join(f"{l}:{c}" for l, c in creator_langs[can].most_common())
        lines.append(f"| {i} | {can} | {canonical_files[can]} | {lang_str} | {var_str} |")
    lines.append("")

    # --- Publishers seen ---
    lines.append("## 4. Publishers presentes\n")
    lines.append("| publisher | n archivos | autores distintos |")
    lines.append("|---|---:|---:|")
    pub_counts = Counter()
    for (cr, pb), n in pair_counts.items():
        pub_counts[pb] += n
    for pb, n in pub_counts.most_common(40):
        lines.append(f"| {pb or '(vacío)'} | {n} | {len(publisher_to_creators.get(pb, []))} |")
    lines.append("")

    # --- Name-variant collisions worth normalizing ---
    lines.append("## 5. Variantes del mismo autor (posibles merges)\n")
    lines.append("_Agrupados por apellido + inicial; revisa si son la misma persona._\n")
    lines.append("| clave apellido+inicial | variantes | n total |")
    lines.append("|---|---|---:|")
    by_key: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for can, n in canonical_files.items():
        if can.startswith("(") or can == "Iglesia de Jesucristo SUD":
            continue
        # key = last token + first initial (crude but effective)
        parts = [p for p in re.split(r"\s+", can) if p]
        if len(parts) < 2:
            continue
        last = norm_key(parts[-1])
        first_initial = norm_key(parts[0])[:1]
        key = f"{last}-{first_initial}"
        by_key[key].append((can, n))
    collisions = [(k, v) for k, v in by_key.items() if len(v) > 1]
    collisions.sort(key=lambda x: -sum(n for _, n in x[1]))
    for k, variants in collisions[:30]:
        var_str = "; ".join(f"{c} ({n})" for c, n in sorted(variants, key=lambda x: -x[1]))
        lines.append(f"| {k} | {var_str} | {sum(n for _, n in variants)} |")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_CSV.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}")
    print(f"  {len(canonical_groups)} autores canónicos de {len(rows)} archivos")
    print(f"  {len(church_pairs)} casos Iglesia SUD")
    print(f"  {len(collisions)} posibles merges de variantes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
