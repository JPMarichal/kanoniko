# Lesson: Never fuzzy-match biographies by token overlap

**Context:** During P4 corpus-expansion cleanup, a fuzzy dedup pass
matched `!Ready/Life of Heber C. Kimball - Orson F. Whitney.epub`
against the already-incorporated `journal-heber-c-kimball` slug because
`{heber, c, kimball}` overlapped ≥3 tokens. The epub was a distinct
biography (Whitney 1888) — a false positive — and got unlinked.

Multiple valuable biographies were lost to the same pattern:
- *Life of John Taylor* (B. H. Roberts 1892)
- *Life of Joseph Smith* (George Q. Cannon 1888)
- *Life and Times of Jesus the Messiah* (Alfred Edersheim 1883)

## Rule — Dedup strategy by material type

| Material type | Matching strategy |
|---|---|
| **Church-authored manuals** (`author: IJCSUD` / "La Iglesia de Jesucristo...") | Fuzzy title match against `corpus/{lang}/manuals/` slugs is OK — author is constant, only the manual matters |
| **Church-authored magazines** | Match by `(magazine, year, month)` derived from filename, against `corpus/{lang}/magazines/<name>/<year>/<month>/` |
| **Individual-author books and biographies** | **Exact (author_norm, title_norm)** match only. Never token-overlap. |
| **Works about the same person by different authors** (biographies, memoirs) | Never auto-dedup — each is a distinct work even if the subject's name dominates the title |

## Anti-patterns

- Token-overlap threshold `>= N` words where proper-name tokens count the same as content words.
- Accepting single-letter tokens (`c`, `w`) as matching tokens.
- Matching across different `category/` roots (e.g., `biographies` ↔ `books`) without author equivalence.

## Recovery

In this incident, the user had backup. Restored from source. Future
passes must never require recovery — the conservative strategy above is
mandatory for any dedup touching `!Ready/`.
