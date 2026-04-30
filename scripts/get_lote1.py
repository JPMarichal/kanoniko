import sys
import os
from pathlib import Path

names = [
    'Aaron Johnson', 'Algernon Sidney Gilbert', 'Almon Babbitt', 
    'Alpheus Cutler', 'Amasa Lyman', 'Amos Davies', 'Ann Lee', 
    'Asa Dodds', 'Brigham Young', 'Burr Riggs'
]
corpus = Path('/mnt/c/own/alejandria/corpus')
results = {n: [] for n in names}

for path in corpus.rglob('*.txt'):
    if 'index' in path.name.lower() or 'concordance' in path.name.lower():
        continue
    try:
        text = path.read_text(encoding='utf-8')
        lower_text = text.lower()
        
        for n in names:
            if n.lower() in lower_text:
                lines = text.split('\n')
                for idx, line in enumerate(lines):
                    if n.lower() in line.lower():
                        ctx = '\n'.join(lines[max(0, idx-2):min(len(lines), idx+3)])
                        out = f"[{path.relative_to(corpus)}]:\n{ctx.strip()}"
                        if out not in results[n]:
                            results[n].append(out)
    except Exception as e:
        pass

for n in names:
    res = results[n]
    if not res: continue
    
    print(f"========== {n.upper()} ==========")
    print(f"Total findings: {len(res)}")
    # If there are too many, print first 15 and last 5 to avoid blowing up stdout
    if len(res) > 20:
        for r in res[:15]:
            print(f"{r}\n---")
        print("... [OMITTED] ...\n---")
        for r in res[-5:]:
            print(f"{r}\n---")
    else:
        for r in res:
            print(f"{r}\n---")
    print("\n")
