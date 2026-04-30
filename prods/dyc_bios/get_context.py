import glob, sys, json
from pathlib import Path

names = [
    "Aaron Johnson", "Algernon Sidney Gilbert", "Almon Babbitt", "Alpheus Cutler",
    "Amasa Lyman", "Amos Davies", "Ann Lee", "Asa Dodds", "Brigham Young", "Burr Riggs"
]

base = Path("c:/own/alejandria/corpus")
files = list(base.glob("es/books/*.txt")) + list(base.glob("es/manuals/*.txt")) + list(base.glob("en/biographies/**/*.txt"))

results = {n: [] for n in names}

for f in files:
    try:
        content = f.read_text(encoding="utf-8")
        paras = content.split('\n\n')
        for p in paras:
            for n in names:
                if n.lower() in p.lower():
                    snippet = p.strip()[:800].replace('\n', ' ')
                    results[n].append(f"[{f.name}] {snippet}")
    except:
        pass

for n in names:
    print(f"\n--- {n} ---")
    for r in results[n][:8]: # max 8 snippets per name
        print(r)
