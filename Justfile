# Alejandria task runner — `just <recipe>` to run.
# Install: https://just.systems

# Use PowerShell on Windows (no Unix sh required); leave POSIX shell elsewhere.
set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# Default: list available recipes.
default:
    @just --list

# Full pipeline: discover → fetch (user) → finalize + commit + catalog update
# Usage: just get_gospelink_book 579
get_gospelink_book contents_id:
    @echo "=== DISCOVER ==="
    python scripts/download_gospelink.py discover --contents-id {{contents_id}} --slug auto
    @echo ""
    @echo "Next steps:"
    @echo "1. Review the summary above"
    @echo "2. Copy the fetch command printed above"
    @echo "3. Run it in PowerShell (captcha may appear)"
    @echo "4. When fetch completes, run: just gospelink_finalize <slug>"

# Audit + enrich-meta + validation + commit + auto-update catalog.
# Runs after user completes fetch in PowerShell.
# Audit + enrich + validate + commit + catalog update.
# Accepts either a slug ("mormon-doctrine") or contents-id ("569").
gospelink_finalize id_or_slug="":
    python scripts/_gospelink_finalize.py {{id_or_slug}}

# One-time login to refresh the Gospelink session cookies.
# Use when data/.gospelink-session.json is missing or > 24h old.
gospelink_bootstrap:
    python scripts/download_gospelink.py bootstrap
