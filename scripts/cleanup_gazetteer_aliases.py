#!/usr/bin/env python3
"""Clean up gazetteer alias problems.

Identifies and fixes:
1. BAD ALIASES: Entry X lists Y as alias, but Y is a DIFFERENT entity
2. REDUNDANT ENTRIES: Entry exists as top-level AND as alias of same entity
3. MERGE CANDIDATES: True spelling variants that should be consolidated

Run with --dry-run to see what would change, or --apply to write changes.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

GAZETTEER = Path("src/alejandria/knowledge/gazetteers/entities.json")

# -----------------------------------------------------------------------
# Manual decisions: entries where the alias relationship is WRONG
# because the name refers to a DIFFERENT entity.
# Format: (alias_name_lower, primary_name, entity_type) -> action
#   "remove_alias" = remove from primary's alias list, keep both entries
#   "keep_both"    = alias is technically correct but both entries are needed
# -----------------------------------------------------------------------
BAD_ALIASES = {
    # Judah the patriarch ≠ Hodevah
    ("judah", "Hodevah", "person"): "remove_alias",
    # Sarah wife of Abraham ≠ Serah daughter of Asher
    ("sarah", "Serah", "person"): "remove_alias",
    # Joseph (BofM) ≠ Joseph Barsabas (Acts)
    ("joseph", "Barsabas", "person"): "remove_alias",
    # Moroni son of Mormon ≠ Captain Moroni the commander
    ("moroni", "Captain Moroni", "person"): "remove_alias",
    # Levi the patriarch ≠ Matthew/Levi the apostle
    ("levi", "Matthew", "person"): "remove_alias",
    # Simeon the patriarch ≠ Simon Peter
    ("simeon", "Simon", "person"): "remove_alias",
    # Zephaniah the prophet ≠ Uriel
    ("zephaniah", "Uriel", "person"): "remove_alias",
    # Ammon (OT/general) ≠ Ammon son of Mosiah specifically
    ("ammon", "Ammon (son of Mosiah)", "person"): "remove_alias",
    # Jacob (BofM, son of Lehi) ≠ Jacob patriarch
    ("jacob", "Jacob (patriarch)", "person"): "remove_alias",
    # Huram (different person with Hupham/Huppim) ≠ Hiram of Tyre
    ("huram", "Hiram", "person"): "remove_alias",
    # Daughter (generic) should not be alias of specific Daughter entries
    ("daughter", "Daughter of Herodias", "person"): "remove_alias",
    ("daughter", "Daughter of Machir", "person"): "remove_alias",
    ("daughter", "Daughter of Meshullam", "person"): "remove_alias",
    ("daughter", "Daughter of Pharaoh", "person"): "remove_alias",
    ("daughter", "Daughter of Shuah", "person"): "remove_alias",
    # Azariah is a common name — multiple different people
    ("azariah", "Jezaniah", "person"): "remove_alias",
    ("azariah", "Uzziah", "person"): "remove_alias",
    # Jehoram king of Israel ≠ Joram king of Judah (they're contemporaries)
    ("jehoram", "Joram", "person"): "remove_alias",
    ("joram", "Jehoram", "person"): "remove_alias",
    # Michal and Merab are SISTERS (Saul's daughters), not the same person
    ("michal", "Merab", "person"): "remove_alias",
    # Naaman the Syrian general ≠ Nohah (son of Benjamin)
    ("naaman", "Nohah", "person"): "remove_alias",
    # Mattaniah could be multiple different people; Zedekiah had Mattaniah as birth name but there are others
    # Shelah son of Judah ≠ Salah (Shelah son of Arphaxad) — different genealogies
    ("shelah", "Salah", "person"): "remove_alias",
    # Seraiah — multiple different people of this name
    ("seraiah", "Shavsha", "person"): "remove_alias",
    # Zechariah — very common name, multiple people
    ("zechariah", "Zacher", "person"): "remove_alias",
    # Eliphelet — multiple people with this name
    ("eliphelet", "Eliphalet", "person"): "keep_both",
    ("eliphelet", "Elpalet", "person"): "keep_both",
    # Heldai — could be different from Heleb and Helem
    ("heldai", "Heleb", "person"): "remove_alias",
    ("heldai", "Helem", "person"): "remove_alias",
    # Cephas as alias of both Peter and Simon — keep both, Cephas is Peter's name
    # but "Simon" as separate entry is Simon the patriarch or other Simons
    # Thaddaeus — alias of both Lebbaeus and Jude (apostle); these may be same person
    # Keep as is, the disambiguation system handles this
    # Judas — alias of Jude and Lebbaeus; there are multiple Judases
    ("judas", "Jude", "person"): "remove_alias",
    ("judas", "Lebbaeus", "person"): "remove_alias",
    # Shammah — different from Shage
    ("shammah", "Shage", "person"): "remove_alias",
    # Rosh — different from Rapha
    ("rosh", "Rapha", "person"): "remove_alias",
    # Sargon ≠ Sennacherib (different Assyrian kings!)
    ("sargon", "Sennacherib", "person"): "remove_alias",
    # Mishael ≠ Meshach (well, actually same person — Mishael's Babylonian name was Meshach)
    # Hananiah ≠ Shadrach (same person — Hananiah's Babylonian name was Shadrach)
    # These are actually correct alias relationships. Keep them.
    # Firstborn [concept] shouldn't be alias of Daughter of Lot
    ("firstborn", "Daughter of Lot - Older", "person"): "remove_alias",
    # Canaanites [people] ≠ Canaan [person] alias
    # Actually this is tricky — Canaanites derives from Canaan. Leave for now.
    # Golgotha and Calvary are the SAME place — keep Golgotha as primary
    ("golgotha", "Calvary", "place"): "keep_both",
    # Sidon the person ≠ Sidon/Zidon the city — different types, so not in scope
    # Endowment [concept] ≠ Temple Endowment [ordinance] — different types, skip
    # Firstborn concept ≠ Daughter of Lot alias
    ("firstborn", "Daughter of Lot - Older", "concept"): "remove_alias",
}

# -----------------------------------------------------------------------
# TRUE SPELLING VARIANTS: same entity, safe to merge into primary
# Format: (entry_name, entry_type) -> primary they should merge into
# The entry's own aliases will be added to the primary.
# -----------------------------------------------------------------------
# These will be computed automatically: entries with no own aliases
# that are pure alias matches and NOT in BAD_ALIASES.


def load_gazetteer():
    with open(GAZETTEER, encoding="utf-8") as f:
        return json.load(f)


def analyze(data):
    """Analyze and return (bad_aliases_to_fix, entries_to_remove, alias_transfers)."""
    # Build lookups
    alias_to_primary = defaultdict(list)
    for etype, entries in data.items():
        for e in entries:
            for a in e.get("aliases", []):
                alias_to_primary[a.lower()].append((etype, e["name"]))

    bad_fixes = []       # (entity_type, primary_name, alias_to_remove)
    to_remove = []       # (entity_type, entry_name)
    alias_transfers = [] # (entity_type, primary_name, aliases_to_add)

    for etype, entries in data.items():
        for e in entries:
            name_lower = e["name"].lower()
            if name_lower not in alias_to_primary:
                continue

            for a_type, a_primary in alias_to_primary[name_lower]:
                if a_type != etype or a_primary.lower() == name_lower:
                    continue

                key = (name_lower, a_primary, etype)

                if key in BAD_ALIASES:
                    action = BAD_ALIASES[key]
                    if action == "remove_alias":
                        bad_fixes.append((etype, a_primary, e["name"]))
                    # "keep_both" = no action needed
                    continue

                # Not in bad list → candidate for merge
                own_aliases = e.get("aliases", [])
                if own_aliases:
                    # Has aliases that would need transferring
                    alias_transfers.append((etype, a_primary, own_aliases))
                to_remove.append((etype, e["name"]))

    return bad_fixes, to_remove, alias_transfers


def apply_fixes(data, bad_fixes, to_remove, alias_transfers):
    """Apply all fixes to the data."""
    changes = {"bad_aliases_fixed": 0, "entries_removed": 0, "aliases_transferred": 0}

    # 1. Fix bad aliases
    for etype, primary_name, alias_to_remove in bad_fixes:
        for e in data[etype]:
            if e["name"] == primary_name:
                aliases = e.get("aliases", [])
                # Remove case-insensitive
                new_aliases = [a for a in aliases if a.lower() != alias_to_remove.lower()]
                if len(new_aliases) < len(aliases):
                    e["aliases"] = new_aliases
                    changes["bad_aliases_fixed"] += 1
                break

    # 2. Transfer aliases from entries being removed to their primaries
    for etype, primary_name, aliases_to_add in alias_transfers:
        for e in data[etype]:
            if e["name"] == primary_name:
                existing = {a.lower() for a in e.get("aliases", [])}
                for a in aliases_to_add:
                    if a.lower() not in existing and a.lower() != primary_name.lower():
                        e.setdefault("aliases", []).append(a)
                        existing.add(a.lower())
                        changes["aliases_transferred"] += 1
                break

    # 3. Remove redundant entries
    remove_set = {(etype, name) for etype, name in to_remove}
    for etype in data:
        before = len(data[etype])
        data[etype] = [e for e in data[etype] if (etype, e["name"]) not in remove_set]
        changes["entries_removed"] += before - len(data[etype])

    return changes


def main():
    dry_run = "--apply" not in sys.argv

    data = load_gazetteer()
    total_before = sum(len(v) for v in data.values())

    bad_fixes, to_remove, alias_transfers = analyze(data)

    print(f"=== Gazetteer Cleanup {'(DRY RUN)' if dry_run else '(APPLYING)'} ===")
    print(f"Total entries before: {total_before}")
    print()

    print(f"Bad aliases to fix: {len(bad_fixes)}")
    for etype, primary, alias in sorted(bad_fixes):
        print(f"  [{etype}] Remove '{alias}' from {primary}'s aliases")
    print()

    print(f"Entries to remove (redundant): {len(to_remove)}")
    for etype, name in sorted(to_remove):
        print(f"  [{etype}] {name}")
    print()

    print(f"Alias transfers (before removal): {len(alias_transfers)}")
    for etype, primary, aliases in sorted(alias_transfers):
        print(f"  [{etype}] Add {aliases} to {primary}")
    print()

    if not dry_run:
        changes = apply_fixes(data, bad_fixes, to_remove, alias_transfers)
        total_after = sum(len(v) for v in data.values())
        print(f"Changes applied:")
        print(f"  Bad aliases fixed: {changes['bad_aliases_fixed']}")
        print(f"  Entries removed: {changes['entries_removed']}")
        print(f"  Aliases transferred: {changes['aliases_transferred']}")
        print(f"  Total entries after: {total_after}")

        with open(GAZETTEER, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"\nWritten to {GAZETTEER}")
    else:
        print("Run with --apply to write changes.")


if __name__ == "__main__":
    main()
