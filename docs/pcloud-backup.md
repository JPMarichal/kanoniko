# DB & Secrets Recovery: pCloud-Based Asset Distribution

The SQLite database (~625 MB compressed) and `.env` secrets are **not stored in git**. They are hosted in pCloud and downloaded via `scripts/pcloud-pull.sh`.

## Quick Start (New Machine)

```bash
git clone https://github.com/JPMarichal/kanoniko.git
cd kanoniko

# Set pCloud download links (or edit the script directly)
export PCLOUD_DB_LINK="https://..."
export PCLOUD_SECRETS_LINK="https://..."

# Download both DB and secrets
bash scripts/pcloud-pull.sh all

# Start the engine
docker compose up --build
```

## pcloud-pull.sh Usage

```bash
bash scripts/pcloud-pull.sh db       # Download SQLite DB only
bash scripts/pcloud-pull.sh secrets   # Download .env secrets only
bash scripts/pcloud-pull.sh all       # Download both
```

The script validates file sizes and auto-decompresses the DB.

## pCloud Setup (One-Time, from Original Machine)

1. Upload `alejandria.db.gz` to pCloud (e.g. `Backups/alejandria/`)
2. Upload `.env` to pCloud (e.g. `Backups/alejandria-secrets/`)
3. Generate a **public download link** for each file
4. To get a direct-download URL from a pCloud public link:
   ```
   https://api.pcloud.com/getpublinkdownload?code=XXXX
   ```
   The response JSON contains `hosts[]` and `path` — combine as `https://{host}{path}`
5. Set the URLs in the script or as env vars

## Updating the DB in pCloud

After a significant indexing run on the GPU machine:

```bash
# 1. Compress the authoritative DB
gzip -k /home/jpmarichal/alejandria-data/sqlite/alejandria.db

# 2. Upload alejandria.db.gz to pCloud (replace the existing file)
#    The public link remains the same if you overwrite in-place
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

For a ~625 MB compressed file:

| Internet speed | Upload (to pCloud) | Download (to new machine) |
|---------------|-------------------|--------------------------|
| 10 Mbps (typical residential upload) | ~8-9 min | — |
| 50 Mbps | ~2 min | ~2 min |
| 100 Mbps | ~1 min | ~1 min |
| 1 Gbps (fiber) | ~5 sec | ~5 sec |

The bottleneck is usually **upload** (residential connections have asymmetric speeds). The prior `gzip` compression step takes ~30-60 seconds on CPU.

## Legacy: Git LFS (Deprecated)

The DB was previously tracked via Git LFS, but GitHub's free tier (1 GB storage + 1 GB bandwidth/month) couldn't sustain a 655 MB file that changes with each indexing run. The LFS tracking in `.gitattributes` may still exist but the object on the server is no longer maintained.

If you see this error on clone, it's expected and harmless:
```
Error downloading object: data/sqlite/alejandria.db.gz (5fc04d2):
  [404] Object does not exist on the server
```

Use `pcloud-pull.sh` instead.

## After DB Is Restored

1. Start Docker Desktop and `docker compose up --build`
2. The DB is bind-mounted into the container
3. Neo4j (KG) can be rebuilt from the DB: `POST /backup/neo4j/restore` or reindex (~3h)
4. Verify: `GET http://localhost:4300/corpus/status`
