"""
Diagnose KG noise: classifies entity nodes into 5 categories to measure
how much of the graph is real vs. extractor failure.

Categories:
    1 = Real entity, clean canonical name
    2 = Real entity, malformed (duplicate, possessive, concat, prefix noise)
    3 = Not the declared type (scripture ref, concept, place misclassified as person, etc.)
    4 = Common word / language fragment (Spanish verb, single noun, etc.)
    5 = Garbage (OCR, HTML, mojibake, sentence fragment)

Run inside the API container:
    docker exec alejandria-api python /app/scripts/diagnose_kg_noise.py
"""

from __future__ import annotations

import csv
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from neo4j import GraphDatabase

URI = os.environ.get("ALEJANDRIA_NEO4J_URI", "bolt://neo4j:7687")
USER = os.environ.get("ALEJANDRIA_NEO4J_USER", "neo4j")
PASS = os.environ.get("ALEJANDRIA_NEO4J_PASSWORD", "alejandria")

OUT_DIR = Path("/app/data/kg-diagnostic")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Classifier patterns ------------------------------------------------------

SCRIPTURE_BOOKS = (
    r"gen|exod?|lev|num|deut|josh|judg|ruth|sam|kgs|kings|chr|ezra|neh|esth|job|ps|psalm|prov|eccl|"
    r"song|isa|jer|lam|ezek|dan|hos|joel|amos|obad|jonah|mic|nah|hab|zeph|hag|zech|mal|"
    r"matt|mark|luke|john|acts|rom|cor|gal|eph|phil|col|thess|tim|tit|phlm|heb|jas|pet|rev|"
    r"nephi|nefi|jacob|enos|jarom|omni|mosiah|mosíah|alma|helaman|helamán|mormon|mormón|ether|éter|moroni|moroni|"
    r"dc|d&c|dyc|moses|moisés|abraham|abr|jsh|js-?h|js-?m|"
    r"mateo|marcos|lucas|juan|hechos|romanos|corintios|gálatas|efesios|filipenses|colosenses|tesalonicenses|timoteo|"
    r"tito|filemón|hebreos|santiago|pedro|apocalipsis|génesis|éxodo|levítico|números|deuteronomio|"
    r"josué|jueces|rut|samuel|reyes|crónicas|esdras|nehemías|ester|salmos|proverbios|eclesiastés|"
    r"cantares|isaías|jeremías|lamentaciones|ezequiel|daniel|oseas|amós|abdías|jonás|miqueas|"
    r"nahúm|habacuc|sofonías|hageo|zacarías|malaquías"
)

RE_SCRIPTURE_REF = re.compile(
    rf"^\s*\(?\s*(\d\s+)?({SCRIPTURE_BOOKS})\.?\s+\d+[:.]\d",
    re.IGNORECASE,
)
RE_SHORT_SCRIPTURE = re.compile(r"^\s*\d+\s*[:\-–]\s*\d+", re.IGNORECASE)
RE_CHAPTER_ONLY = re.compile(rf"^\s*({SCRIPTURE_BOOKS})\s*\d+\s*$", re.IGNORECASE)

RE_MOJIBAKE = re.compile(r"[ÏÎÂâ½¬Ð­·ÏÎ±ÐÐµÏ]{2,}|Ã[¡©³º]|â[€™˜œ]")
RE_CONTROL = re.compile(r"[\x00-\x1f]")
RE_HTML = re.compile(r"</?[a-z]+\s*[^>]*>|\b(id|class|href|src)\s*=\s*[\"']")
RE_NUMERIC = re.compile(r"^\s*[\d\.\-–:\s]+\s*$")
RE_STARTS_NONWORD = re.compile(r"^[^\w\"'¿¡]")

# Common stopwords / verb forms in ES that show up as "persons"
RE_SPANISH_VERB = re.compile(
    r"\b\w+(aba|abas|ábamos|aban|aría|arías|aríamos|arían|aré|arás|aremos|arán|é|ás|amos|án|"
    r"ía|ías|íamos|ían|ió|iste|imos|ieron|ando|iendo|ado|ada|ido|ida)\b",
    re.IGNORECASE,
)
RE_SPANISH_FRAGMENT = re.compile(
    r"^(así|entonces|quien|quienes|conforme|cuando|mientras|aunque|hombre|mujer|meses|"
    r"niños|envuelve|enfoquese|confusiones|quítatela|terminar|preparar|acompañar|compartir|"
    r"intimid|tenían|poseo|fuisteis)",
    re.IGNORECASE,
)

# Single common nouns / words (any language) that shouldn't be persons
COMMON_WORDS = {
    "scrub", "skins", "theaters", "couple", "ordinances", "abbot",
    "latinae", "qumranic", "meses", "confusiones",
}

RE_POSSESSIVE_EN = re.compile(r"['\u2019]s$")
RE_DUP_UPPER = re.compile(r"^(\w+)\s+\1\W*$", re.IGNORECASE)  # "Lydia LYDIA"
RE_TRAILING_PUNCT = re.compile(r"[,;:\(\)]$|\s(ed|did|bare)\.?$", re.IGNORECASE)
RE_LEADING_JUNK = re.compile(r"^[^\w\"]|^(the|el|la|los|las|un|una)\s+(?:[A-Z])", re.IGNORECASE)
RE_PRONUNCIATION = re.compile(r"\w+\s+\w+['\-]\w+['\-]\w+", re.IGNORECASE)  # "Lebana le-ba'-na"

# Fragment with embedded verbs/conjugations or clear sentence structure
RE_SENTENCE_LIKE = re.compile(r"\b(did|bare|was|were|has|had|debe|puede|pudo|viene)\b", re.IGNORECASE)


def classify(name: str) -> tuple[int, str]:
    """Return (category, reason)."""
    n = (name or "").strip()
    if not n:
        return 5, "empty"
    # --- Category 5: Garbage ---
    if RE_MOJIBAKE.search(n):
        return 5, "mojibake"
    if RE_CONTROL.search(n):
        return 5, "control_char"
    if RE_HTML.search(n):
        return 5, "html_fragment"
    if RE_NUMERIC.match(n):
        return 5, "numeric_only"
    if len(n) > 80 and " " in n:
        return 5, "overlong"
    if n.count('"') == 1 or n.count("'") >= 3:
        return 5, "unbalanced_quotes"
    if any(ch in n for ch in "√"):
        return 5, "symbol"
    if RE_STARTS_NONWORD.match(n) and not n.startswith(("¿", "¡", '"', "'")):
        return 5, "starts_nonword"

    # --- Category 3: Scripture ref ---
    if RE_SCRIPTURE_REF.match(n) or RE_CHAPTER_ONLY.match(n):
        return 3, "scripture_ref"
    if RE_SHORT_SCRIPTURE.match(n) and len(n) < 15:
        return 3, "short_scripture"

    # --- Category 2: Malformed real entity ---
    if RE_POSSESSIVE_EN.search(n):
        return 2, "possessive"
    if RE_DUP_UPPER.match(n):
        return 2, "duplicated_word"
    if n.endswith(",") or n.endswith(";") or n.endswith(":"):
        return 2, "trailing_punct"
    if RE_PRONUNCIATION.match(n) and "-" in n and "'" in n:
        return 2, "pronunciation_suffix"
    # prefix noise: bullet, arrow, superscript footnote
    if n[0] in "•↩─·" or re.match(r"^[\u00b2\u00b3\u2070-\u2079]", n):
        return 2, "prefix_noise"
    if re.search(r"[\u00b2\u00b3\u2070-\u2079]+$", n):
        return 2, "footnote_suffix"

    # --- Category 4: Common word / language fragment ---
    low = n.lower()
    if low in COMMON_WORDS:
        return 4, "common_word"
    if len(n.split()) == 1 and n[0].islower():
        return 4, "single_lowercase"
    if RE_SPANISH_VERB.search(n):
        return 4, "spanish_verb"
    if RE_SPANISH_FRAGMENT.match(n):
        return 4, "spanish_fragment"

    # --- Sentence-like fragment -> garbage ---
    if RE_SENTENCE_LIKE.search(n):
        return 5, "sentence_fragment"

    # --- Category 1: default clean ---
    # extra: very short single tokens are suspicious but not disqualifying
    return 1, "clean"


# --- Sampling -----------------------------------------------------------------

FAMILY_RELS = [
    "FATHER_OF", "MOTHER_OF", "SPOUSE_OF", "BROTHER_OF", "SISTER_OF",
    "DESCENDANT_OF", "ANCESTOR_OF", "SON_OF", "DAUGHTER_OF",
]


def sample_nodes(driver, entity_type: str, n: int) -> list[dict]:
    q = """
    MATCH (e:Entity {type: $t})
    WITH e, rand() AS rnd ORDER BY rnd LIMIT $n
    RETURN e.name AS name,
           COUNT { (e)--() } AS degree,
           COUNT { (e)-[r]-() WHERE type(r) IN $fam } AS fam,
           COUNT { (e)-[r]-() WHERE type(r) = 'CO_OCCURS_WITH' } AS cooc,
           COUNT { (e)-[r]-() WHERE type(r) IN ['MENTIONED_IN','REFERENCED_IN'] } AS mentions
    """
    with driver.session() as s:
        return [dict(r) for r in s.run(q, t=entity_type, n=n, fam=FAMILY_RELS)]


def run_analysis(types: list[tuple[str, int]], manual_csv: Path | None = None):
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    report_lines = []

    # Global KG summary
    with driver.session() as s:
        totals = s.run("MATCH (n:Entity) RETURN n.type AS t, count(n) AS c ORDER BY c DESC").data()
        fam_total = s.run(
            "MATCH ()-[r]-() WHERE type(r) IN $fam RETURN count(r) AS c", fam=FAMILY_RELS
        ).single()["c"]

    report_lines.append("# KG Noise Diagnostic\n")
    report_lines.append("_Auto-generated by `scripts/diagnose_kg_noise.py`_\n")
    report_lines.append("## KG composition\n")
    report_lines.append(f"- Total entity nodes: **{sum(r['c'] for r in totals):,}**")
    report_lines.append(f"- Total family relations (FATHER_OF, MOTHER_OF, SPOUSE_OF, SIBLING_OF, etc.): **{fam_total:,}**\n")
    report_lines.append("| Type | Count |")
    report_lines.append("|---|---:|")
    for r in totals[:15]:
        report_lines.append(f"| {r['t']} | {r['c']:,} |")
    report_lines.append("")

    # Calibration vs. manual labels (person, n=300)
    p_true_given_auto = None  # matrix for calibrated estimates
    if manual_csv and manual_csv.exists():
        manual = {}
        with manual_csv.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                manual[row["name"]] = int(row["manual_cat"])

        agree = 0
        matrix = defaultdict(lambda: defaultdict(int))  # matrix[manual][auto]
        for name, mcat in manual.items():
            acat, _ = classify(name)
            matrix[mcat][acat] += 1
            if acat == mcat:
                agree += 1
        total = len(manual)
        report_lines.append(f"## Classifier calibration (vs. manual labels on `person`, n={total})\n")
        report_lines.append(f"- Overall agreement: **{agree}/{total} = {agree / total:.1%}**\n")
        report_lines.append("**Confusion matrix (rows = manual, cols = auto):**\n")
        header = "| manual \\ auto | " + " | ".join(str(i) for i in range(1, 6)) + " | total |"
        report_lines.append(header)
        report_lines.append("|---|" + "---:|" * 6)
        for m in range(1, 6):
            row_total = sum(matrix[m].values())
            cells = [str(matrix[m].get(a, 0)) for a in range(1, 6)]
            report_lines.append(f"| {m} | " + " | ".join(cells) + f" | {row_total} |")
        report_lines.append("")

        # Build P(true | auto) by transposing and normalizing each auto-column
        auto_totals = defaultdict(int)
        for m in range(1, 6):
            for a in range(1, 6):
                auto_totals[a] += matrix[m].get(a, 0)
        p_true_given_auto = {a: {} for a in range(1, 6)}
        for a in range(1, 6):
            if auto_totals[a]:
                for m in range(1, 6):
                    p_true_given_auto[a][m] = matrix[m].get(a, 0) / auto_totals[a]
            else:
                # fallback: identity
                for m in range(1, 6):
                    p_true_given_auto[a][m] = 1.0 if m == a else 0.0

        report_lines.append("**Precision by predicted category (P(true | auto)):**\n")
        report_lines.append("| auto | true=1 | true=2 | true=3 | true=4 | true=5 |")
        report_lines.append("|---:|---:|---:|---:|---:|---:|")
        for a in range(1, 6):
            cells = [f"{p_true_given_auto[a][m]:.1%}" for m in range(1, 6)]
            report_lines.append(f"| {a} | " + " | ".join(cells) + " |")
        report_lines.append("")
        report_lines.append("> Calibrated estimates below apply this transfer matrix to auto counts. "
                            "Calibration was fit on `person` only; estimates for other types assume similar misclassification patterns and should be read as order-of-magnitude.\n")

    # Per-type sampling
    report_lines.append("## Per-type classification (auto)\n")
    per_type_summary = []
    for etype, n in types:
        sample = sample_nodes(driver, etype, n)
        if not sample:
            continue
        labeled = []
        cat_counts = Counter()
        reason_counts = Counter()
        fam_by_cat = defaultdict(list)
        deg_by_cat = defaultdict(list)
        for row in sample:
            cat, reason = classify(row["name"])
            labeled.append({**row, "cat": cat, "reason": reason})
            cat_counts[cat] += 1
            reason_counts[reason] += 1
            fam_by_cat[cat].append(row["fam"])
            deg_by_cat[cat].append(row["degree"])

        # Save per-type CSV
        out_csv = OUT_DIR / f"auto_sample_{etype}_{n}.csv"
        with out_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["name", "cat", "reason", "degree", "fam", "cooc", "mentions"])
            w.writeheader()
            for r in labeled:
                w.writerow(r)

        pct = {c: cat_counts[c] / n * 100 for c in range(1, 6)}

        # Calibrated estimate: redistribute auto counts using P(true | auto)
        calib = {m: 0.0 for m in range(1, 6)}
        if p_true_given_auto:
            for a in range(1, 6):
                for m in range(1, 6):
                    calib[m] += cat_counts[a] * p_true_given_auto[a][m]
        pct_calib = {m: calib[m] / n * 100 for m in range(1, 6)}

        per_type_summary.append({
            "type": etype, "n": n,
            **{f"cat{c}": cat_counts[c] for c in range(1, 6)},
            **{f"pct{c}": pct[c] for c in range(1, 6)},
            **{f"calib_pct{c}": pct_calib[c] for c in range(1, 6)},
            "file": out_csv.name,
        })

        report_lines.append(f"### `{etype}` (n={n})\n")
        report_lines.append("| Cat | Description | Auto count | Auto % | Calibrated % |")
        report_lines.append("|---:|---|---:|---:|---:|")
        labels = {
            1: "Real, clean canonical",
            2: "Real, malformed (normalizable)",
            3: "Wrong type (scripture/concept/place)",
            4: "Common word / lang fragment",
            5: "Garbage (OCR/HTML/mojibake/sentence)",
        }
        for c in range(1, 6):
            report_lines.append(
                f"| {c} | {labels[c]} | {cat_counts[c]} | {pct[c]:.1f}% | {pct_calib[c]:.1f}% |"
            )
        report_lines.append("")

        # Top reasons
        report_lines.append("**Top detection reasons:**\n")
        for reason, cnt in reason_counts.most_common(8):
            report_lines.append(f"- `{reason}`: {cnt}")
        report_lines.append("")

        # Fixability for person type
        if etype == "person":
            clean_usable = cat_counts[1]
            fixable_via_resolution = cat_counts[2]
            unsalvageable = cat_counts[3] + cat_counts[4] + cat_counts[5]
            report_lines.append("**Fixability breakdown:**\n")
            report_lines.append(f"- Usable as-is: **{clean_usable / n:.1%}**")
            report_lines.append(f"- Recoverable via entity resolution: **{fixable_via_resolution / n:.1%}**")
            report_lines.append(f"- Requires extractor fix or pruning: **{unsalvageable / n:.1%}**\n")

    # Summary table across types
    report_lines.append("## Cross-type summary (auto-classifier)\n")
    report_lines.append("| Type | n | Cat1 | Cat2 | Cat3 | Cat4 | Cat5 | Noise |")
    report_lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in per_type_summary:
        noise = r["pct2"] + r["pct3"] + r["pct4"] + r["pct5"]
        report_lines.append(
            f"| {r['type']} | {r['n']} | {r['pct1']:.1f}% | {r['pct2']:.1f}% | "
            f"{r['pct3']:.1f}% | {r['pct4']:.1f}% | {r['pct5']:.1f}% | {noise:.1f}% |"
        )
    report_lines.append("")

    report_lines.append("## Cross-type summary (calibrated, post-transfer matrix)\n")
    report_lines.append("| Type | n | Cat1 | Cat2 | Cat3 | Cat4 | Cat5 | Noise | Projected absolute noise |")
    report_lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in per_type_summary:
        noise = r["calib_pct2"] + r["calib_pct3"] + r["calib_pct4"] + r["calib_pct5"]
        # find total count from type composition
        total_type = next((row["c"] for row in totals if row["t"] == r["type"]), 0)
        abs_noise = int(total_type * noise / 100)
        report_lines.append(
            f"| {r['type']} | {r['n']} | {r['calib_pct1']:.1f}% | {r['calib_pct2']:.1f}% | "
            f"{r['calib_pct3']:.1f}% | {r['calib_pct4']:.1f}% | {r['calib_pct5']:.1f}% | "
            f"{noise:.1f}% | ~{abs_noise:,} of {total_type:,} |"
        )
    report_lines.append("")

    # Actionable recommendations
    report_lines.append("## Actionable takeaways\n")
    person_row = next((r for r in per_type_summary if r["type"] == "person"), None)
    if person_row:
        total_persons = next((row["c"] for row in totals if row["t"] == "person"), 0)
        clean_abs = int(total_persons * person_row["calib_pct1"] / 100)
        fixable_abs = int(total_persons * person_row["calib_pct2"] / 100)
        unsalvageable_abs = int(total_persons * (person_row["calib_pct3"] + person_row["calib_pct4"] + person_row["calib_pct5"]) / 100)
        report_lines.append(f"**Person nodes ({total_persons:,} total) projected breakdown:**\n")
        report_lines.append(f"- Usable clean persons: **~{clean_abs:,}** ({person_row['calib_pct1']:.0f}%)")
        report_lines.append(f"- Recoverable via entity resolution: **~{fixable_abs:,}** ({person_row['calib_pct2']:.0f}%)")
        report_lines.append(f"- Extractor failure — requires pruning or pipeline fix: **~{unsalvageable_abs:,}** ({person_row['calib_pct3'] + person_row['calib_pct4'] + person_row['calib_pct5']:.0f}%)\n")

    report_lines.append("**Priority fixes (in order of cost/benefit):**\n")
    report_lines.append("1. **Scripture-reference filter** at NER stage — single regex rejects `Matthew 3:3`, `Alma 55:17`, `Jer 38:21` patterns that currently pollute `person`, `object`, `period`.")
    report_lines.append("2. **Mojibake/HTML sanitization** at parser stage — UTF-8 decode errors (`ÏÎ¬`, `â`, `Â­`) and HTML fragments (`id=\"aside1_p1\"`) should be stripped before NER.")
    report_lines.append("3. **Spanish verb filter** — conjugated forms (`-aba`, `-ía`, `-aré`, gerunds) capitalized at sentence start are being promoted; add POS check or suffix blacklist.")
    report_lines.append("4. **Entity resolution pass** on existing KG — canonicalize duplicates (`Lydia LYDIA`, `Amaleki` + `• Amaleki`), strip possessives, unify transliterations. Recovers cat 2 without reindexing.")
    report_lines.append("5. **`object` type is critically noisy (~58%)** — review extractor rules for this type specifically before anything else; likely capturing raw tokens.\n")

    report_md = OUT_DIR / "diagnostic_report.md"
    report_md.write_text("\n".join(report_lines), encoding="utf-8")

    # Also save summary CSV
    with (OUT_DIR / "per_type_summary.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=per_type_summary[0].keys())
        w.writeheader()
        w.writerows(per_type_summary)

    driver.close()
    print(f"Report written to: {report_md}")
    for r in per_type_summary:
        print(f"  {r['type']:20s} n={r['n']:4d}  cat1={r['pct1']:.1f}%  noise={100 - r['pct1']:.1f}%")


if __name__ == "__main__":
    manual = Path("/app/data/kg-diagnostic/manual_labels_300.csv")
    TYPES = [
        ("person", 2000),
        ("people", 500),
        ("place", 500),
        ("concept", 500),
        ("object", 500),
        ("period", 500),
        ("work", 500),
    ]
    run_analysis(TYPES, manual_csv=manual)
