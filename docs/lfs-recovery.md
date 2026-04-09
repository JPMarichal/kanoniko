# LFS Recovery: SQLite DB Transfer Between Machines

The SQLite database (`data/sqlite/alejandria.db.gz`) is tracked via Git LFS (~625 MB compressed). When cloning on a new machine, the LFS object may fail to download (404) if the push from the original machine was incomplete or GitHub LFS quota was exceeded.

## Diagnosis

On the new machine, after clone:
```
Error downloading object: data/sqlite/alejandria.db.gz (5fc04d2):
  [404] Object does not exist on the server
```

This means code and corpus are intact, but the DB (FTS + vectors + KG source data) is missing.

## Recovery: Push from Original Machine

Run these steps on the machine that has the authoritative DB.

```bash
# 1. Verify the DB exists
ls -lh /home/jpmarichal/alejandria-data/sqlite/alejandria.db

# 2. Go to the repo
cd /ruta/al/repo/kanoniko    # adjust path

# 3. Verify LFS is installed and tracking works
git lfs install
git lfs track

# 4. List LFS objects in the local repo
git lfs ls-files

# 5. Check if .db.gz is a real file or an orphan pointer (~130 bytes)
file data/sqlite/alejandria.db.gz
ls -lh data/sqlite/alejandria.db.gz

# 6. If it's an orphan pointer, regenerate from the container DB
gzip -k /home/jpmarichal/alejandria-data/sqlite/alejandria.db
cp /home/jpmarichal/alejandria-data/sqlite/alejandria.db.gz data/sqlite/

# 7. Push ALL LFS objects to remote
git lfs push --all origin

# 8. Verify upload succeeded
git lfs ls-files --all
```

## Recovery: Pull on New Machine

After the push succeeds on the original machine:

```bash
# 9. Download the LFS object
cd D:\myapps\kanoniko
git lfs pull

# 10. Verify it's the real file, not a pointer
ls -lh data/sqlite/alejandria.db.gz
# Should be ~625 MB, not 130 bytes

# 11. Decompress
gunzip -k data/sqlite/alejandria.db.gz
```

## If GitHub LFS Quota Is Exhausted

GitHub Free gives 1 GB storage + 1 GB bandwidth/month. A 655 MB file nearly maxes both.

Alternatives:
- Transfer `alejandria.db.gz` via OneDrive, USB, or direct network copy
- Place it in `data/sqlite/` and run `gunzip -k` to get the raw `.db`
- Consider a self-hosted LFS server or upgrading GitHub LFS quota

## After DB Is Restored

1. Start Docker Desktop and `docker compose up --build`
2. The DB is bind-mounted into the container
3. Neo4j (KG) can be rebuilt from the DB: `POST /backup/neo4j/restore` or reindex (~3h)
4. Verify: `GET http://localhost:4300/corpus/status`
