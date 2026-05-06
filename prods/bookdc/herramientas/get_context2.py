import glob, sys, json
from pathlib import Path

names = [
    "Calves Wilson", "Charles C. Rich", "Daniel Miles", "Daniel Stanton",
    "David Dort", "David Fullmer", "David W. Patten", "David Whitmer",
    "Don C. Smith", "Dunbar Wilson"
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
    for r in results[n][:5]: # limit exactly what we need
        print(r)
