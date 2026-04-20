# Alejandria task runner — `just <recipe>` to run.
# Install: https://just.systems

# Default: list available recipes.
default:
    @just --list

# Discover a Gospelink work by contents-id, derive slug + metadata, and
# print the suggested fetch command. The user runs the printed fetch in
# PowerShell (interactive captcha required), then `just gospelink_finalize`.
get_gospelink_book contents_id:
    python scripts/download_gospelink.py discover --contents-id {{contents_id}} --slug auto

# Audit + enrich-meta + content validation after a fetch completes.
# Aborts if any WAF leak or structural issue is found.
gospelink_finalize slug:
    python scripts/download_gospelink.py audit --slug {{slug}} --write-redo
    python scripts/download_gospelink.py enrich-meta --slug {{slug}}
    python scripts/_gospelink_validate.py {{slug}}
    @echo ""
    @echo "Validation passed. To commit, run: just gospelink_commit {{slug}}"

# Stage and commit the corpus folder for a Gospelink slug.
gospelink_commit slug:
    python scripts/_gospelink_commit.py {{slug}}

# One-time login to refresh the Gospelink session cookies.
# Use when data/.gospelink-session.json is missing or > 24h old.
gospelink_bootstrap:
    python scripts/download_gospelink.py bootstrap
