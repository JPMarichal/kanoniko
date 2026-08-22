import os, json, subprocess, sys

corpus_dir = "corpus/personajes"

result = subprocess.run(
    [
        "docker",
        "exec",
        "wp_bc",
        "wp",
        "post",
        "list",
        "--post_type=bc_quote_author",
        "--posts_per_page=1000",
        "--format=json",
        "--allow-root",
    ],
    capture_output=True,
    text=True,
    shell=False,
)
posts = json.loads(result.stdout)


def title_to_slug(title):
    slug = title.lower()
    for a, b in [
        ("\u00e1", "a"),
        ("\u00e9", "e"),
        ("\u00ed", "i"),
        ("\u00f3", "o"),
        ("\u00fa", "u"),
        ("\u00f1", "n"),
        ("\u00fc", "u"),
    ]:
        slug = slug.replace(a, b)
    slug = "".join(c if c.isalnum() else "-" for c in slug)
    slug = "-".join(p for p in slug.split("-") if p)
    return slug


PRESIDENTS = [
    (112, "joseph-smith"),
    (117, "joseph-f-smith"),
    (118, "heber-j-grant"),
    (120, "david-o-mckay"),
    (121, "joseph-fielding-smith"),
    (122, "harold-b-lee"),
    (123, "spencer-w-kimball"),
    (124, "ezra-taft-benson"),
    (125, "howard-w-hunter"),
    (93, "gordon-b-hinckley"),
    (126, "thomas-s-monson"),
    (127, "russell-m-nelson"),
]
DONE = {
    "brigham-young",
    "john-taylor",
    "wilford-woodruff",
    "lorenzo-snow",
    "george-albert-smith",
}

EARLY = [
    (206, "hyrum-smith"),
    (3165, "oliver-cowdery"),
    (3166, "david-whitmer"),
    (3167, "martin-harris"),
    (3144, "sidney-rigdon"),
    (3258, "emma-smith"),
    (200, "orson-pratt"),
    (202, "orson-hyde"),
    (192, "willard-richards"),
    (197, "william-smith"),
    (3149, "william-law"),
    (181, "john-henry-smith"),
    (3147, "john-smith"),
    (160, "matthew-cowley"),
    (188, "erastus-snow"),
    (184, "albert-carrington"),
    (183, "moses-thatcher"),
    (173, "rudger-clawson"),
    (172, "reed-smoot"),
    (180, "george-teasdale"),
    (3168, "edward-partridge"),
    (3169, "isaac-morley"),
    (3170, "john-corrill"),
    (309, "newel-k-whitney"),
    (3260, "elizabeth-ann-whitney"),
    (191, "lyman-wight"),
    (351, "james-e-talmage"),
    (350, "b-h-roberts"),
]

MODERN = [
    (140, "ulisses-soares"),
    (141, "patrick-kearon"),
    (128, "dallin-h-oaks"),
    (129, "henry-b-eyring"),
    (130, "jeffrey-r-holland"),
    (131, "dieter-f-uchtdorf"),
    (132, "david-a-bednar"),
    (133, "quentin-l-cook"),
    (134, "d-todd-christofferson"),
    (135, "neil-l-andersen"),
    (136, "ronald-a-rasband"),
    (137, "gary-e-stevenson"),
    (138, "dale-g-renlund"),
    (139, "gerrit-w-gong"),
]


def corpus_status(slug):
    path = os.path.join(corpus_dir, slug)
    if not os.path.isdir(path):
        return "\u274c"  # cross mark
    files = os.listdir(path)
    has_ldsorg = "ldsorg.html" in files
    has_wiki = "wikipedia.html" in files
    has_qid = "wikidata.json" in files
    if has_ldsorg and has_wiki and has_qid:
        return "\u2705"  # check mark
    if has_wiki and has_qid:
        return "\u26a0\ufe0f"  # warning
    return "\u274c"


def find_title(pid):
    for p in posts:
        if p["ID"] == str(pid):
            return p["post_title"]
    return f"ID {pid}"


def make_batches(people, prefix_batch_num):
    batches = []
    current = []
    for pid, slug in people:
        current.append((pid, slug, corpus_status(slug), find_title(pid)))
        if len(current) == 5:
            batches.append(current)
            current = []
    if current:
        batches.append(current)
    return batches


# Build plan doc
lines = []
lines.append("# Plan de Lotes — Biograf\u00edas")
lines.append("")
lines.append(
    f"> {len(posts)} personas en bc_quote_author. Pendientes: ~{len(posts) - 9}."
)
lines.append("> Organizado por prioridad hist\u00f3rica, 5 por lote.")
lines.append(">")
lines.append("> **Leyenda**:")
lines.append("> - \u2705 = corpus completo (ldsorg+wiki+qid)")
lines.append("> - \u26a0\ufe0f = corpus parcial (wiki+qid, sin ldsorg)")
lines.append("> - \u274c = sin corpus en disco (descargar fuentes primero)")
lines.append("")

# Lote 1
lines.append("## Lote 1 — COMPLETADO")
lines.append("")
lines.append("| # | ID | Persona | Corpus | Estado |")
lines.append("|---|----|---------|--------|--------|")
done_list = [
    (113, "brigham-young", "Brigham Young"),
    (114, "john-taylor", "John Taylor"),
    (115, "wilford-woodruff", "Wilford Woodruff"),
    (116, "lorenzo-snow", "Lorenzo Snow"),
    (119, "george-albert-smith", "George Albert Smith"),
]
for i, (pid, slug, title) in enumerate(done_list, 1):
    lines.append(f"| {i} | {pid} | {title} | \u2705 | \u2705 Publicado |")
lines.append("")

# Build remaining batches
pres_remaining = [(pid, slug) for pid, slug in PRESIDENTS if slug not in DONE]
hist_remaining = [(pid, slug) for pid, slug in EARLY]
mod_remaining = [(pid, slug) for pid, slug in MODERN]

all_priority = pres_remaining + hist_remaining + mod_remaining

# Add remaining posts that have ldsorg
remaining_with_ldsorg = []
for p in posts:
    pid = int(p["ID"])
    title = p["post_title"]
    slug = title_to_slug(title)
    if slug in DONE:
        continue
    path = os.path.join(corpus_dir, slug)
    if os.path.isdir(path) and "ldsorg.html" in os.listdir(path):
        already = False
        for apid, aslug in all_priority:
            if aslug == slug:
                already = True
                break
        if not already:
            remaining_with_ldsorg.append((pid, slug))

# Now build scheduled batches
scheduled = []
current = []


def flush_batch():
    global scheduled, current
    if current:
        scheduled.append(current)
        current = []


for pid, slug in all_priority:
    current.append((pid, slug, corpus_status(slug), find_title(pid)))
    if len(current) == 5:
        flush_batch()

# Fill remaining slots in last batch with ldsorg people
if current and len(current) < 5:
    needed = 5 - len(current)
    for pid, slug in remaining_with_ldsorg:
        if needed == 0:
            break
        current.append((pid, slug, corpus_status(slug), find_title(pid)))
        needed -= 1
    flush_batch()

# More batches from ldsorg people
remaining_pool = [(pid, slug) for pid, slug in remaining_with_ldsorg]
# Check already used
used_slugs = set()
for batch in scheduled:
    for pid, slug, _, _ in batch:
        used_slugs.add(slug)

remaining_pool = [
    (pid, slug) for pid, slug in remaining_with_ldsorg if slug not in used_slugs
]

for pid, slug in remaining_pool:
    current.append((pid, slug, corpus_status(slug), find_title(pid)))
    if len(current) == 5:
        flush_batch()
if current:
    scheduled.append(current)

# Determine tier titles
tier_titles = {}
current_tier = 0
tier_map = {
    0: "PRESIDENTES DE LA IGLESIA",
    1: "FIGURAS HIST\u00d3RICAS FUNDACIONALES",
    2: "AP\u00d3STOLES MODERNOS (Primera Presidencia y Cu\u00f3rum de los Doce)",
}
# After priority, all are GENERAL
for i, batch in enumerate(scheduled):
    tier_label = tier_map.get(i, "AUTORIDADES GENERALES Y L\u00cdDERES AUXILIARES")
    lines.append(f"## Lote {i + 2}: {tier_label}")
    lines.append("")
    lines.append("| # | ID | Persona | Corpus | Estado |")
    lines.append("|---|----|---------|--------|--------|")
    for j, (pid, slug, status, title) in enumerate(batch, 1):
        lines.append(f"| {j} | {pid} | {title} | {status} | Pendiente |")
    lines.append("")

# Summary
total_batches = 1 + len(scheduled)
total_people = 5 + sum(len(b) for b in scheduled)
lines.append("---")
lines.append("")
lines.append(f"## Resumen")
lines.append("")
lines.append(
    f"- **Total lotes planificados**: {total_batches - 1} pendientes (m\u00e1s los que sigan despu\u00e9s)"
)
lines.append(f"- **Personas cubiertas en el plan**: {total_people}")
lines.append(
    f"- **Personas a\u00fan no cubiertas** (sin ldsorg ni prioridad): ~{len(posts) - total_people}"
)
lines.append("")
lines.append(
    "Las personas no cubiertas en este plan se procesar\u00e1n en lotes posteriores"
)
lines.append(
    "a medida que se descarguen sus fuentes, siguiendo la prioridad del skill biografia-persona."
)

with open("docs/plan-lotes.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Plan escrito a docs/plan-lotes.md")
print(f"Total lotes planificados (sin contar Lote 1): {len(scheduled)}")
print(f"Siguiente lote:")
for pid, slug, status, title in scheduled[0]:
    print(f"  ID {pid}: {title} ({status})")
