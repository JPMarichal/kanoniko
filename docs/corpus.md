# Corpus Structure

The corpus is a bilingual collection of LDS Church literature, bind-mounted at the `corpus/` directory. It is **never containerized** — it lives on the host filesystem and is the first thing that scales independently.

## Directory Layout

```
corpus/
├── en/                          # English
│   ├── scriptures/
│   │   ├── ot/                  # Old Testament
│   │   │   ├── genesis/
│   │   │   │   ├── 1.txt
│   │   │   │   ├── 2.txt
│   │   │   │   └── ...
│   │   │   ├── exodus/
│   │   │   └── ...
│   │   ├── nt/                  # New Testament
│   │   ├── bom/                 # Book of Mormon
│   │   ├── dc-testament/        # Doctrine and Covenants
│   │   │   └── dc/
│   │   │       ├── 1.txt        # Section 1
│   │   │       └── ...
│   │   └── pgp/                 # Pearl of Great Price
│   │       ├── moses/
│   │       ├── abraham/
│   │       ├── js-matthew/
│   │       ├── js-history/
│   │       └── articles-of-faith/
│   ├── general-conference/      # General Conference talks
│   ├── manuals/                 # Church manuals
│   ├── biographies/             # Biographical works
│   └── web/                     # Web downloads
├── es/                          # Spanish (same structure)
│   ├── scriptures/
│   └── ...
```

## Scripture File Format

Each scripture file represents one chapter (or section for D&C). Verses are numbered at the start of each line:

```
1 In the beginning God created the heaven and the earth.
2 And the earth was without form, and void; and darkness was upon the face of the deep.
3 And the Spirit of God moved upon the face of the waters.
```

## Structural Differences Between Volumes

| Volume | Unit | Naming | Notes |
|--------|------|--------|-------|
| Old Testament | Chapter | `genesis/1.txt` | Standard chapters |
| New Testament | Chapter | `matthew/1.txt` | Standard chapters |
| Book of Mormon | Chapter | `1-nephi/1.txt` | Hyphenated book names |
| D&C | Section | `dc/1.txt` | Sections, not chapters |
| PGP | Chapter | `moses/1.txt` | Mixed: Moses (8 ch), Abraham (5 ch), JS-M (1 ch), JS-H (1 ch), AoF (1 art) |

### Special Cases
- **D&C Official Declarations**: `dc/od1.txt`, `dc/od2.txt` — no verse numbers
- **PGP Facsimiles**: Abraham includes facsimile descriptions
- **Articles of Faith**: Single chapter with 13 articles as verses

## Citation Formats

The system generates scripture references per chunk:

| Language | Example |
|----------|---------|
| English | `Genesis 1:1-5`, `1 Nephi 3:7`, `D&C 76:22-24` |
| Spanish | `Génesis 1:1-5`, `1 Nefi 3:7`, `DyC 76:22-24` |

Both short and long citation forms coexist:
- Short: `D&C 76:22` / `DyC 76:22`
- Long: `Doctrine and Covenants 76:22` / `Doctrina y Convenios 76:22`

## Supported File Formats

| Extension | Parser | Used By |
|-----------|--------|---------|
| `.txt` | Plain text | Scriptures |
| `.md` | Markdown (stripped) | Conference talks, manuals |
| `.html` | HTML (stripped tags) | Web downloads |
| `.json` | JSON (text extraction) | Structured data |

## Downloading Scriptures

```bash
REQUESTS_CA_BUNDLE=docker/ca-certificates.crt python scripts/download_scriptures.py
```

This downloads all standard works in both English and Spanish from the Church's content API.
