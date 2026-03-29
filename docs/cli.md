# Command-Line Interface

Click-based CLI for searching the corpus and managing the system.

## Installation

The CLI is installed as the `alejandria` command via `pyproject.toml` entry points.

## Commands

### Search

```bash
# Full-text search
alejandria text "faith repentance" -n 10

# Semantic search
alejandria semantic "plan of salvation" -n 10

# Hybrid search
alejandria hybrid "baptism of Jesus" --text-weight 0.4 --semantic-weight 0.6

# All search commands support:
#   -n, --limit       Max results (default 10)
#   -s, --source      Filter by corpus subdirectory
#   --json            Output raw JSON
```

### Chat (RAG)

```bash
# Ask a question
alejandria ask "Who was Nephi?"

# With source filter and JSON output
alejandria ask "What is the plan of salvation?" -s scriptures --json
```

### Knowledge Graph

```bash
# Find entities
alejandria graph find "Moses" -t person

# Get entity connections
alejandria graph neighbors "Jesus Christ" -d 2 -n 50

# Graph statistics
alejandria graph summary
```

### System

```bash
# System status
alejandria status

# Run indexing
alejandria index

# Full reindex
alejandria index --full

# Version
alejandria --version
```

## Output Formats

All commands support `--json` flag for machine-readable output. Default output is human-friendly text.

## Implementation

`src/alejandria/cli.py` — Click command group with lazy-loaded dependencies (services only initialize when their commands are invoked).
