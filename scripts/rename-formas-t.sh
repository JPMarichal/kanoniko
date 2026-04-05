#!/usr/bin/env bash
# Rename all Formas T to standard: {CCCC}-{slug-coleccion}-{FF}-{slug}.md
# Collection 0002: senda-de-los-convenios (7 groups, 54 forms)
# Collection 0003: vidas (6 forms)
# Also normalizes frontmatter: collection, collection_id, group, collection_order

DIR="/c/own/alejandria/prods/formas-t"
DRY_RUN="${1:-false}"

# ── Group offsets within collection 0002 ──
# senda:          8 forms, offset 0  → 01-08
# bautismo:       8 forms, offset 8  → 09-16
# espiritu-santo: 7 forms, offset 16 → 17-23
# santa-cena:     8 forms, offset 24 → 24-31
# sacerdocio:    11 forms, offset 32 → 32-42
# investidura:    7 forms, offset 43 → 43-49
# sellamiento:    5 forms, offset 49 → 50-54

declare -A GROUP_OFFSET
GROUP_OFFSET[senda-de-los-convenios]=0
GROUP_OFFSET[bautismo]=8
GROUP_OFFSET[espiritu-santo]=16
GROUP_OFFSET[santa-cena]=23
GROUP_OFFSET[sacerdocio]=31
GROUP_OFFSET[investidura]=42
GROUP_OFFSET[sellamiento]=49

# Map frontmatter collection value → group slug for frontmatter
declare -A GROUP_SLUG
GROUP_SLUG[senda-de-los-convenios]="senda"
GROUP_SLUG[bautismo]="bautismo"
GROUP_SLUG[espiritu-santo]="espiritu-santo"
GROUP_SLUG[santa-cena]="santa-cena"
GROUP_SLUG[sacerdocio]="sacerdocio"
GROUP_SLUG[investidura]="investidura"
GROUP_SLUG[sellamiento]="sellamiento"

# File prefix to strip for form slug
declare -A FILE_PREFIX
FILE_PREFIX[senda-de-los-convenios]="senda-"
FILE_PREFIX[bautismo]="bautismo-"
FILE_PREFIX[espiritu-santo]="espiritu-santo-"
FILE_PREFIX[santa-cena]="santa-cena-"
FILE_PREFIX[sacerdocio]="sacerdocio-"
FILE_PREFIX[investidura]="investidura-"
FILE_PREFIX[sellamiento]="sellamiento-"

echo "=== Formas T Rename (mode: $DRY_RUN) ==="
echo ""

count=0
errors=0

for f in "$DIR"/*.md; do
    basename_full=$(basename "$f")
    basename_noext=$(basename "$f" .md)

    # Skip already-renamed (0001-*) and template
    [[ "$basename_noext" =~ ^[0-9]{4}- ]] && continue
    [[ "$basename_noext" == "_template" ]] && continue

    # Extract frontmatter fields
    collection=$(grep '^collection:' "$f" | sed 's/collection: *//;s/"//g' | tr -d '\r')
    order=$(grep '^collection_order:' "$f" | sed 's/collection_order: *//;s/"//g' | tr -d '\r')

    if [[ -z "$collection" || -z "$order" ]]; then
        echo "SKIP: $basename_full (missing collection or order)"
        ((errors++))
        continue
    fi

    # ── Vidas collection (0003) ──
    if [[ "$collection" == "vidas" ]]; then
        form_slug=$(echo "$basename_noext" | sed 's/-vida$//')
        fnum=$(printf "%02d" "$order")
        newname="0003-vidas-${fnum}-${form_slug}.md"

        if [[ "$DRY_RUN" == "true" ]]; then
            echo "OK: $basename_full -> $newname  [0003/vidas, order=$order]"
        else
            # Normalize frontmatter
            sed -i "s/^collection:.*/collection: vidas/" "$f"
            if ! grep -q 'collection_id:' "$f"; then
                sed -i "/^collection:/a collection_id: \"0003\"" "$f"
            else
                sed -i "s/^collection_id:.*/collection_id: \"0003\"/" "$f"
            fi
            if ! grep -q '^group:' "$f"; then
                sed -i "/^collection_id:/a group: \"vidas\"" "$f"
            fi
            mv "$f" "$DIR/$newname"
            echo "OK: $basename_full -> $newname"
        fi
        ((count++))
        continue
    fi

    # ── Senda-de-los-convenios collection (0002) ──
    offset="${GROUP_OFFSET[$collection]}"
    gslug="${GROUP_SLUG[$collection]}"
    prefix="${FILE_PREFIX[$collection]}"

    if [[ -z "$offset" ]]; then
        echo "SKIP: $basename_full (unknown collection: $collection)"
        ((errors++))
        continue
    fi

    # Calculate global form number within collection
    global_num=$((offset + order))
    fnum=$(printf "%02d" "$global_num")

    # Strip file prefix to get form slug
    form_slug="${basename_noext#$prefix}"

    newname="0002-senda-${fnum}-${form_slug}.md"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "OK: $basename_full -> $newname  [0002/senda-de-los-convenios, group=$gslug, order=$global_num]"
    else
        # Normalize frontmatter: collection → senda-de-los-convenios
        sed -i "s/^collection:.*/collection: senda-de-los-convenios/" "$f"
        if ! grep -q 'collection_id:' "$f"; then
            sed -i "/^collection:/a collection_id: \"0002\"" "$f"
        else
            sed -i "s/^collection_id:.*/collection_id: \"0002\"/" "$f"
        fi
        if ! grep -q '^group:' "$f"; then
            sed -i "/^collection_id:/a group: \"$gslug\"" "$f"
        else
            sed -i "s/^group:.*/group: \"$gslug\"/" "$f"
        fi
        # Update collection_order to global number
        sed -i "s/^collection_order:.*/collection_order: $global_num/" "$f"
        mv "$f" "$DIR/$newname"
        echo "OK: $basename_full -> $newname"
    fi
    ((count++))
done

echo ""
echo "Done: $count renamed, $errors skipped"
