#!/usr/bin/env python
"""Theme 5: Literature — ARCHIVE ONLY (user: 'no tiene valor directo para el corpus').

Moves 28 works directly from !Ready to !Done without incorporation.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"

ARCHIVE = [
    # Theme 5 singletons
    "Amaury - Alexandre Dumas.epub",
    "American Hobo in Europe _ A True Narrative of the Adan at Home and in the Old Country, An - Ben Goodkind.epub",
    "Anna Karenina - Leo Tolstoy.epub",
    "Anne of Avonlea - Lucy M. Montgomery.epub",
    "Anne of Green Gables - Lucy M Montgomery.epub",
    "At the Back of the North Wind - George Macdonald.epub",
    "Book of Thel - William Blake.epub",
    "Child_s Garden of Verses - Robert Louis Stevenson.epub",
    "Danger at Mormon Crossing _ Sandy Steele Adventures #2 - Robert Leckie.epub",
    "Don Quixote - Miguel Cervantes.epub",
    "Dymer - Clive Hamilton.epub",
    "Emma - Jane Austen.epub",
    "First Fam'lies of the Sierras - Joaquin Miller.epub",
    "Four Arthurian Romances - Chrétien de Troyes.epub",
    "Gulliver_s Travels - Jonathan Swift.epub",
    "Heap o_ Livin_ - Edgar A Guest.epub",
    "Heritage of the Desert_ A Novel, The - Zane Grey.epub",
    "House of the Seven Gables - Nathaniel Hawthorne.epub",
    "Idylls of the King - Alfred Tennyson.epub",
    "Ivanhoe - Walter Scott.epub",
    "Lament of the Mormon Wife_ A Poem, The - Marietta Holley.epub",
    "Last of the Mohicans - James Fenimore Cooper.epub",
    # Previously deferred (Kipling 2, Verne 2, Dostoevsky 2)
    "Around the World in Eighty Days - Jules Verne.epub",
    "Brothers Karamazov - Fyodor Dostoevsky.epub",
    "Crime and Punishment - Fyodor Dostoevsky.epub",
    "Journey to the Center of the Earth - Jules Verne.epub",
    "Jungle Book - Rudyard Kipling.epub",
    "Just So Stories - Rudyard Kipling.epub",
]

archived = 0
missing = []
for fn in ARCHIVE:
    src = READY / fn
    if src.exists():
        src.rename(DONE / fn)
        archived += 1
        print(f"  archived: {fn[:70]}")
    else:
        missing.append(fn)
        print(f"  MISSING: {fn[:70]}")

print(f"\nTheme 5 (Literature archive): {archived}/{len(ARCHIVE)} archived")
for m in missing:
    print(f"  - {m[:70]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")
