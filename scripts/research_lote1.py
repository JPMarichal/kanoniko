import os
from pathlib import Path

names = [
    'Aaron Johnson', 'Algernon Sidney Gilbert', 'Almon Babbitt',
    'Alpheus Cutler', 'Amasa Lyman', 'Amos Davies', 'Ann Lee',
    'Asa Dodds', 'Brigham Young', 'Burr Riggs'
]
corpus = Path("corpus")

if not corpus.exists():
    print("Corpus directory not found")
    exit(1)

out_dir = Path("prods/dyc_bios/research")
out_dir.mkdir(parents=True, exist_ok=True)

for name in names:
    print(f"SEARCHING: {name}")
    found = 0
    with open(out_dir / f"{name}.txt", "w", encoding="utf-8") as out:
        for p in corpus.rglob("*.txt"):
            p_str = str(p).lower()
            if "index" in p_str or "concordance" in p_str or "journal-of-discourses" in p_str or "dictionary" in p_str:
                continue
            try:
                text = p.read_text(encoding="utf-8")
                if name.lower() in text.lower():
                    lines = text.split("\n")
                    for idx, line in enumerate(lines):
                        if name.lower() in line.lower():
                            start = max(0, idx-2)
                            end = min(len(lines), idx+3)
                            ctx = "\n".join(lines[start:end])
                            out.write(f"[{p}]\n{ctx}\n---\n")
                            found += 1
            except:
                pass
    print(f"[{name}] Total findings: {found}")
