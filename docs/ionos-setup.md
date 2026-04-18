# IONOS VPS — Postgres setup for Alejandría (Fase 0)

Guía paso a paso para provisionar el Postgres 16 + pgvector en el IONOS VPS M (2 vCore / 4 GB RAM / 160 GB NVMe) y dejar aplicado el DDL de Alejandría desde la máquina local.

Al terminar, tendrás:
- Postgres 16 corriendo como systemd service en el VPS
- pgvector + pg_trgm + unaccent instaladas
- Base `alejandria` con el schema vivo (mismo DDL del bench)
- Dos usuarios: `alejandria_rw` y `alejandria_ro`
- TLS habilitado (Let's Encrypt si hay dominio, self-signed si no)
- Firewall que solo acepta 5432 desde tus IPs
- Cron de `pg_dump` diario cifrado

> **Supuesto del manual:** Ubuntu 24.04 LTS. IONOS lo ofrece como imagen; se reinstala desde la consola en ~5 min. Para CentOS/Debian los nombres de paquetes cambian pero la estructura es la misma.

---

## 0. Prerrequisitos (antes de empezar)

Antes de tocar el VPS, decide y prepara esto en la máquina local:

| Cosa | Qué es / dónde conseguirlo |
|---|---|
| **SSH key pair** | `ssh-keygen -t ed25519 -f ~/.ssh/ionos_alejandria -C "alejandria@vps"`. Guarda la clave pública; la pegas en la consola IONOS en el paso 1. |
| **Dominio (opcional pero recomendado)** | Un registro A/AAAA que apunte al VPS (ej. `alejandria.tudominio.com`). Si no tienes, se puede empezar con self-signed y migrar después. |
| **Tu IP pública actual** | `curl -4 ifconfig.me` en cada máquina desde donde te vas a conectar. Son las IPs que abriremos en el firewall. Si es dinámica, considera usar rangos de tu ISP o aceptar ajustes periódicos. |
| **Password seguro para `postgres` y `alejandria_rw`** | Genera con `openssl rand -base64 24`. Anótalos en tu password manager. |

---

## 1. Reinstalar / preparar el VPS desde la consola IONOS

1. Login en https://cloud.ionos.com
2. **Compute Engine → Servers → tu VPS M → Reinstall**
3. Elige imagen **Ubuntu 24.04 LTS** (o **Ubuntu 22.04** si prefieres; la guía funciona en ambos).
4. En **SSH keys**, pega la clave pública generada en el paso 0.
5. Confirma reinstall (borra todo lo que hubiera — si tienes datos valiosos, hacer backup antes).
6. Espera ~5 min hasta que IONOS muestre el VPS como "Running".
7. Copia la **IP pública IPv4** del VPS — la usas en los siguientes pasos.

## 2. Primera conexión + hardening básico

Desde tu máquina local:

```bash
ssh -i ~/.ssh/ionos_alejandria root@<IP_DEL_VPS>
```

Dentro del VPS (como root):

```bash
# 2.1 Actualizar todo
apt update && apt upgrade -y

# 2.2 Crear usuario no-root con sudo
adduser --gecos "" alejandria
usermod -aG sudo alejandria
mkdir -p /home/alejandria/.ssh
cp /root/.ssh/authorized_keys /home/alejandria/.ssh/
chown -R alejandria:alejandria /home/alejandria/.ssh
chmod 700 /home/alejandria/.ssh
chmod 600 /home/alejandria/.ssh/authorized_keys

# 2.3 Deshabilitar login root por SSH + password auth
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart ssh

# 2.4 Firewall base (UFW)
apt install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw --force enable

# 2.5 Fail2ban para SSH
apt install -y fail2ban
systemctl enable --now fail2ban

# 2.6 Hostname + locale (opcional)
hostnamectl set-hostname alejandria-pg
timedatectl set-timezone UTC
```

Cierra la sesión y vuelve a conectarte como usuario normal para confirmar:

```bash
# En local
ssh -i ~/.ssh/ionos_alejandria alejandria@<IP_DEL_VPS>
```

Confirma con `sudo -v` que tienes sudo.

## 3. Instalar Postgres 16 (repo oficial PGDG)

Desde el VPS como `alejandria`:

```bash
# 3.1 Repo oficial PostgreSQL
sudo install -d /usr/share/postgresql-common/pgdg
sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
  --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc
sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] \
  https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
  > /etc/apt/sources.list.d/pgdg.list'
sudo apt update

# 3.2 Instalar Postgres 16 + extensiones
sudo apt install -y postgresql-16 postgresql-contrib-16 postgresql-16-pgvector

# 3.3 Confirmar que arrancó
sudo systemctl status postgresql@16-main --no-pager
```

## 4. Tunear `postgresql.conf` para 4 GB RAM

```bash
sudo -u postgres nano /etc/postgresql/16/main/postgresql.conf
```

Aplica estos valores (busca cada uno y descomenta + ajusta):

```conf
# --- Memoria (calibrado para 4 GB RAM total) ---
shared_buffers = 1GB
effective_cache_size = 2500MB
work_mem = 32MB
maintenance_work_mem = 512MB

# --- WAL y checkpoints ---
max_wal_size = 2GB
checkpoint_timeout = 15min

# --- I/O (NVMe) ---
random_page_cost = 1.1
effective_io_concurrency = 200

# --- Red ---
listen_addresses = '*'
port = 5432

# --- SSL/TLS (los cert paths se configuran en paso 7) ---
ssl = on
```

**No reinicies aún** — primero configuramos `pg_hba.conf` y TLS.

## 5. Crear la base, los usuarios y las extensiones

Como `postgres`:

```bash
sudo -u postgres psql <<SQL
-- Base
CREATE DATABASE alejandria;

-- Usuario read-write (lo usa la app y los migradores)
CREATE USER alejandria_rw WITH PASSWORD 'REEMPLAZA_CON_openssl_rand_base64_24';
GRANT ALL PRIVILEGES ON DATABASE alejandria TO alejandria_rw;

-- Usuario read-only (para queries de monitoreo / dashboards futuros)
CREATE USER alejandria_ro WITH PASSWORD 'REEMPLAZA_CON_OTRO_openssl_rand_base64_24';
GRANT CONNECT ON DATABASE alejandria TO alejandria_ro;

-- Cambia el password del superuser postgres
ALTER USER postgres WITH PASSWORD 'REEMPLAZA_CON_OTRO_openssl_rand_base64_24';

\c alejandria
GRANT ALL ON SCHEMA public TO alejandria_rw;
GRANT USAGE ON SCHEMA public TO alejandria_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO alejandria_ro;

-- Extensiones (necesarias para el DDL)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
SQL
```

## 6. `pg_hba.conf` — quién puede conectarse

```bash
sudo -u postgres nano /etc/postgresql/16/main/pg_hba.conf
```

Al final del archivo, **antes** de cualquier línea `host all all 0.0.0.0/0 ...`, añade:

```conf
# Conexiones de Alejandría (reemplaza por tus IPs reales del paso 0)
hostssl alejandria  alejandria_rw  <TU_IP_LAPTOP>/32          scram-sha-256
hostssl alejandria  alejandria_rw  <TU_IP_PERSONAL>/32        scram-sha-256
hostssl alejandria  alejandria_ro  <TU_IP_LAPTOP>/32          scram-sha-256
```

**Importante**: `hostssl` (no `host`) fuerza TLS. Sin TLS el rechazo es automático.

## 7. Certificados TLS

### Opción A — Let's Encrypt (recomendado, requiere dominio)

```bash
sudo apt install -y certbot

# Detiene Postgres y abre 80 temporalmente para el challenge
sudo ufw allow 80/tcp
sudo systemctl stop postgresql@16-main

# Generar cert (reemplaza con tu dominio real)
sudo certbot certonly --standalone -d alejandria.tudominio.com \
  --agree-tos -m tu-email@dominio.com --no-eff-email

# Mover certs a donde postgres los pueda leer
sudo mkdir -p /etc/postgresql/16/main/certs
sudo cp /etc/letsencrypt/live/alejandria.tudominio.com/fullchain.pem \
  /etc/postgresql/16/main/certs/server.crt
sudo cp /etc/letsencrypt/live/alejandria.tudominio.com/privkey.pem \
  /etc/postgresql/16/main/certs/server.key
sudo chown postgres:postgres /etc/postgresql/16/main/certs/*
sudo chmod 600 /etc/postgresql/16/main/certs/server.key
sudo chmod 644 /etc/postgresql/16/main/certs/server.crt

# Cerrar puerto 80 (no lo necesitamos salvo para renovación)
sudo ufw delete allow 80/tcp
```

Automatizar renovación con hook que recopia a postgres:

```bash
sudo tee /etc/letsencrypt/renewal-hooks/deploy/postgres-copy.sh > /dev/null <<'EOF'
#!/bin/bash
set -e
DOMAIN=alejandria.tudominio.com
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/postgresql/16/main/certs/server.crt
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/postgresql/16/main/certs/server.key
chown postgres:postgres /etc/postgresql/16/main/certs/*
chmod 600 /etc/postgresql/16/main/certs/server.key
chmod 644 /etc/postgresql/16/main/certs/server.crt
systemctl reload postgresql@16-main
EOF
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/postgres-copy.sh
```

### Opción B — Self-signed (sin dominio)

```bash
sudo mkdir -p /etc/postgresql/16/main/certs
cd /etc/postgresql/16/main/certs
sudo openssl req -new -x509 -days 730 -nodes -text \
  -out server.crt -keyout server.key \
  -subj "/CN=<IP_DEL_VPS>"
sudo chown postgres:postgres server.*
sudo chmod 600 server.key
sudo chmod 644 server.crt
```

**Desventaja**: el cliente necesitará `sslmode=require` (no `verify-full`) porque la CA no está validada. Menos seguro; migra a Opción A cuando tengas dominio.

### Configurar los paths en `postgresql.conf`

```bash
sudo -u postgres nano /etc/postgresql/16/main/postgresql.conf
```

Cerca del final:

```conf
ssl = on
ssl_cert_file = '/etc/postgresql/16/main/certs/server.crt'
ssl_key_file = '/etc/postgresql/16/main/certs/server.key'
```

## 8. Abrir 5432 solo a tus IPs + arrancar Postgres

```bash
# Firewall — sustituir por tus IPs reales (paso 0)
sudo ufw allow from <TU_IP_LAPTOP> to any port 5432 proto tcp comment 'Alejandria laptop'
sudo ufw allow from <TU_IP_PERSONAL> to any port 5432 proto tcp comment 'Alejandria home'

# Arrancar Postgres
sudo systemctl enable postgresql@16-main
sudo systemctl start postgresql@16-main
sudo systemctl status postgresql@16-main --no-pager
```

Verificar desde dentro del VPS:

```bash
sudo -u postgres psql -c "SHOW ssl;"
# Debe devolver: on
```

## 9. Test de conexión remota (desde la máquina local)

```bash
# Instalar cliente si no lo tienes (Windows: via pgadmin o psql.exe; WSL Ubuntu: apt)
wsl -d Ubuntu-20.04 sudo apt install -y postgresql-client-16

# Conectar (Opción A — Let's Encrypt)
PGPASSWORD='<password_rw>' psql "host=alejandria.tudominio.com port=5432 \
  dbname=alejandria user=alejandria_rw sslmode=verify-full"

# Conectar (Opción B — self-signed)
PGPASSWORD='<password_rw>' psql "host=<IP_DEL_VPS> port=5432 \
  dbname=alejandria user=alejandria_rw sslmode=require"

# Test básico
\c alejandria
SELECT version();
SELECT extname FROM pg_extension;
\q
```

Si esto funciona, **estás listo para aplicar el DDL desde la máquina local**.

## 10. Aplicar el DDL de Alejandría desde local

Desde el repo en la laptop:

```bash
# En Ubuntu-20.04 WSL (per feedback_docker_engine)
wsl -d Ubuntu-20.04 bash -c "docker run --rm \
  -v /mnt/c/own/alejandria:/app -w /app -e PYTHONPATH=/app/src \
  -e ALEJANDRIA_POSTGRES_HOST=alejandria.tudominio.com \
  -e ALEJANDRIA_POSTGRES_PORT=5432 \
  -e ALEJANDRIA_POSTGRES_USER=alejandria_rw \
  -e ALEJANDRIA_POSTGRES_PASSWORD='<password_rw>' \
  -e ALEJANDRIA_POSTGRES_DB=alejandria \
  -e ALEJANDRIA_POSTGRES_SSLMODE=verify-full \
  python:3.12-slim bash -c 'pip install -q psycopg[binary] pydantic-settings && python -c \"
from alejandria.storage.postgres.schema import apply_schema, current_version
v = apply_schema(notes=\\\"first apply on IONOS VPS\\\")
print(f\\\"Schema applied — version={v}\\\")
print(f\\\"current_version(): {current_version()}\\\")
\"'"
```

Debería imprimir `Schema applied — version=1` y dejar las 9 tablas listas.

## 11. Backups automáticos con `pg_dump`

En el VPS:

```bash
# 11.1 Estructura
sudo mkdir -p /var/backups/alejandria
sudo chown postgres:postgres /var/backups/alejandria

# 11.2 Script de backup (cifrado con GPG)
sudo -u postgres tee /usr/local/bin/alejandria-backup.sh > /dev/null <<'EOF'
#!/bin/bash
set -euo pipefail
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT="/var/backups/alejandria/alejandria-${STAMP}.sql.gz"
pg_dump -Fc alejandria | gzip > "$OUT"
# Rotar: conservar últimos 14 días
find /var/backups/alejandria -name "alejandria-*.sql.gz" -mtime +14 -delete
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  backup  ${OUT}  $(du -h "$OUT" | cut -f1)" \
  >> /var/backups/alejandria/backup.log
EOF
sudo chmod +x /usr/local/bin/alejandria-backup.sh
sudo chown postgres:postgres /usr/local/bin/alejandria-backup.sh

# 11.3 Cron diario a las 03:15 UTC
echo "15 3 * * * /usr/local/bin/alejandria-backup.sh" | sudo -u postgres crontab -

# 11.4 Verifica
sudo -u postgres /usr/local/bin/alejandria-backup.sh
ls -lh /var/backups/alejandria/
```

**Opcional — sync backups a tu máquina local** con `rsync` + cron en local, o publicarlos a una ubicación remota cifrada (S3 / B2 / WebDAV).

## 12. Checklist final

```bash
# En el VPS
sudo systemctl is-active postgresql@16-main           # active
sudo ufw status | grep 5432                             # solo tus IPs
sudo -u postgres psql -c "SHOW ssl"                     # on
sudo -u postgres psql -c "SELECT extname FROM pg_extension WHERE extname IN ('vector','pg_trgm','unaccent')"

# Desde local
psql "host=... sslmode=verify-full ..." -c "\dt"        # 9 tablas
```

Cuando los 4 checks pasan, **Fase 0 de IONOS está completa**. El próximo paso es re-correr los migradores (SQLite → + Neo4j →) apuntando a este VPS en lugar del bench local, luego repetir R0 + R7 para llegar al estado limpio que ya validamos.

---

## Troubleshooting común

| Síntoma | Causa probable | Fix |
|---|---|---|
| `connection refused` al puerto 5432 | listen_addresses = 'localhost' | Cambiar a `'*'` + reload |
| `no pg_hba.conf entry` | IP no en la whitelist | Añadir línea `hostssl ... <IP>/32` + reload |
| `SSL SYSCALL error` | cert ilegible por postgres | Verificar `chown postgres:postgres` + `chmod 600 server.key` |
| `could not translate host name` | DNS no resuelve | `dig alejandria.tudominio.com` desde local; revisa registro A |
| Postgres OOM | shared_buffers demasiado alto | Bajar a 768MB y reiniciar |

## Referencias

- PGDG APT repo: https://wiki.postgresql.org/wiki/Apt
- pgvector: https://github.com/pgvector/pgvector
- Let's Encrypt para Postgres: https://www.postgresql.org/docs/current/ssl-tcp.html
- `postgresql.conf` tuning: https://pgtune.leopard.in.ua (introducir 4 GB + SSD + Web app)
