# DB & Secrets Recovery: GitHub Releases

The SQLite database (~1.4 GB compressed) and `.env` secrets are **not stored in git**. They are hosted as GitHub Release assets and downloaded via `scripts/backup-pull.sh`.

## Quick Start (New Machine)

```bash
git clone https://github.com/JPMarichal/kanoniko.git
cd kanoniko

# Download DB and encrypted secrets from latest release
bash scripts/backup-pull.sh all

# Decrypt secrets (requires passphrase)
openssl enc -aes-256-cbc -d -pbkdf2 -in data/sqlite/env.enc -out docker/.env -pass pass:YOUR_PASSPHRASE

# Start the engine
docker compose up --build
```

## backup-pull.sh Usage

```bash
bash scripts/backup-pull.sh db       # Download SQLite DB only
bash scripts/backup-pull.sh secrets   # Download encrypted .env only
bash scripts/backup-pull.sh all       # Download both
```

The script downloads from the latest `backup-*` release, validates file sizes, and auto-decompresses the DB.

## Creating a Backup (After Indexing)

From the development machine (Windows + WSL GPU):

```bash
# 1. Compress the authoritative DB from the GPU container
wsl -d Ubuntu-20.04 bash -c "gzip -kf /home/jpmarichal/alejandria-data/sqlite/alejandria.db"

# 2. Copy to Windows
wsl -d Ubuntu-20.04 bash -c "cp /home/jpmarichal/alejandria-data/sqlite/alejandria.db.gz /mnt/c/own/alejandria/data/sqlite/"

# 3. Encrypt secrets
wsl -d Ubuntu-20.04 bash -c "openssl enc -aes-256-cbc -salt -pbkdf2 -in /home/jpmarichal/alejandria-repo/docker/.env -out /tmp/env.enc -pass pass:PASSPHRASE && cp /tmp/env.enc /mnt/c/own/alejandria/data/sqlite/env.enc && rm /tmp/env.enc"

# 4. Create release (or update existing)
gh release create backup-YYYY-MM-DD data/sqlite/alejandria.db.gz data/sqlite/env.enc \
  --title "DB Backup YYYY-MM-DD" \
  --notes "SQLite backup. Includes FTS chunks, sqlite-vec vectors, and all indexed corpus data." \
  --prerelease

# 5. Clean up local encrypted file
rm -f data/sqlite/env.enc
```

## When to Back Up

The DB only changes when new material is indexed. Back up based on events, not a fixed schedule:

| Event | Backup needed? |
|-------|---------------|
| After a large indexing batch (e.g. Liahona 19K articles) | **Yes, immediately** |
| After adding a few files incrementally | Optional — reindexing a few files is cheap (~2-3 sec/file) |
| Code-only changes (no indexing) | No — the DB didn't change |
| Before migrating to a new machine | **Yes** |

**In practice:** after each significant indexing session. Typically 1-2 times per week during active corpus expansion, rarely during code-only development.

## Transfer Time Estimates

For a ~1.4 GB compressed file:

| Internet speed | Upload (gh release) | Download |
|---------------|-------------------|----------|
| 10 Mbps (typical residential upload) | ~19 min | — |
| 50 Mbps | ~4 min | ~4 min |
| 100 Mbps | ~2 min | ~2 min |
| 1 Gbps (fiber) | ~12 sec | ~12 sec |

## Security Notes

- **DB (`alejandria.db.gz`):** Public. Contains only indexed corpus text (scriptures, talks, manuals) — no secrets.
- **Secrets (`env.enc`):** AES-256-CBC encrypted with OpenSSL (PBKDF2 key derivation). Safe to host publicly; requires passphrase to decrypt.
- The passphrase is **never stored in git** — share it through a secure channel.

## Legacy Methods (Deprecated)

### pCloud (deprecated 2026-04)
Previously used pCloud public links via `scripts/pcloud-pull.sh`. Abandoned because corporate proxy blocked uploads. The script may still exist but is no longer maintained.

### Git LFS (deprecated 2025)
GitHub's free tier (1 GB storage + 1 GB bandwidth/month) couldn't sustain the DB file. GitHub Releases have no such limits for public repos.

## After DB Is Restored

1. Start containers: `docker compose up --build`
2. The DB is bind-mounted into the container
3. Neo4j (KG) can be rebuilt from the DB: `POST /backup/neo4j/restore` or reindex (~3h)
4. Verify: `GET http://localhost:4300/corpus/status`
