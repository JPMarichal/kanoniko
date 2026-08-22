# IONOS VPS — Postgres setup for Alejandría (Fase 0)

Guía paso a paso para provisionar el Postgres 16 + pgvector en el IONOS VPS M (2 vCore / 4 GB RAM / 160 GB NVMe) y dejar aplicado el DDL de Alejandría desde la máquina local.

## ⚙️ Configuración concreta de este entorno (abril 2026)

| Parámetro | Valor |
|---|---|
| VPS IP (IONOS) | `212.227.243.210` |
| OS | Ubuntu 22.04.5 LTS (jammy) |
| DB vecina (ya existente) | **MariaDB 10.6.23**, puerto 3306, DB `ccm` (1.1 MB) |
| Puerto Postgres (nuevo) | `5432` |
| IP pública de la laptop de trabajo | `163.116.231.24` |
| IP pública de la máquina personal | *pendiente — añadir cuando se use* |
| TLS | self-signed (sin dominio por ahora) |
| Base de datos Postgres | `alejandria` |
| Usuario read-write | `alejandria_rw` |
| Usuario read-only | `alejandria_ro` |
| RAM total | 3.8 GB |
| RAM disponible antes de Postgres | ~500 MB (MariaDB usa ~3 GB) |
| Swap | 4 GB file (añadido antes de Postgres) |
| Disco libre | 60 GB / 155 GB |

**Escenario "VPS con MariaDB existente":** este VPS ya tiene MariaDB productiva (DB `ccm`) en puerto 3306. Postgres se instala **en paralelo** en 5432 sin tocar MariaDB. Las dos DBs coexisten. Saltar el paso 1a (reinstall) es obligatorio.

> **Nota sobre el `.env` del repo:** declara `DB_NAME=alejandria` pero la MariaDB real tiene `ccm`. El `.env` es aspiracional o referencia a otro servicio — no afecta este setup. La Postgres nueva puede usar `alejandria` sin colisión porque vive en puerto distinto.

**Consecuencia operacional: RAM apretada.** Con MariaDB consumiendo ~3 GB, solo quedan ~500 MB antes de instalar Postgres. Dos decisiones derivadas:

1. **Añadir 4 GB de swap ANTES de Postgres** (fase 1.5). Sin swap, un OOM-killer puede matar MariaDB bajo pico de carga.
2. **Tuning reducido** de Postgres vs el benchmark (que corría en un VPS dedicado). Ver fase 4 con los valores ajustados.

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

Antes de tocar el VPS, prepara esto en la máquina local:

| Cosa | Este entorno |
|---|---|
| **SSH al VPS** | Ya existe (se usa para administrar MySQL). Verifica con `ssh <usuario>@212.227.243.210`. |
| **IP pública de la laptop** | `163.116.231.24` (confirmada el 2026-04-18). Re-verifica con `curl -s -4 ifconfig.me` antes del firewall. Si tu ISP te cambia la IP, habrá que actualizar `pg_hba.conf` y UFW. |
| **Password para los 3 usuarios Postgres** | Genera 3 distintos con `openssl rand -base64 24` — uno para `postgres` (superuser), uno para `alejandria_rw`, uno para `alejandria_ro`. Guárdalos en tu password manager **antes** del paso 5. |
| **Snapshot defensivo del MySQL** | Ver paso 1b — no sigas si no tienes backup del MySQL productivo. |

---

## 1. Preparar el VPS

### Opción 1a — VPS nuevo / reinstalar (solo si NO tienes datos productivos)

1. Login en https://cloud.ionos.com
2. **Compute Engine → Servers → tu VPS M → Reinstall**
3. Elige imagen **Ubuntu 24.04 LTS** (o **Ubuntu 22.04** si prefieres).
4. En **SSH keys**, pega la clave pública generada en el paso 0.
5. Confirma reinstall (borra todo — si tienes datos valiosos, hacer backup antes).
6. Espera ~5 min hasta que IONOS muestre el VPS como "Running".
7. Copia la **IP pública IPv4** del VPS — la usas en los siguientes pasos.

### Opción 1b — VPS con MySQL u otros servicios ya productivos (CASO ACTUAL)

**No reinstales.** El VPS tiene MySQL productivo en puerto 3306 con datos reales — un reinstall los borra. Postgres se instala al lado:

1. Verifica que tienes acceso SSH actual (probablemente ya lo tienes si estás administrando MySQL):
   ```bash
   ssh <tu_usuario>@212.227.243.210
   ```
2. Confirma el OS del VPS:
   ```bash
   lsb_release -a
   cat /etc/os-release
   ```
   La guía asume Ubuntu 20.04/22.04/24.04 o Debian. Si es CentOS / otro, cambian los nombres de paquete (`dnf` en vez de `apt`, `postgresql-server` en vez de `postgresql-16`, etc.).
3. Verifica que MySQL está corriendo y no lo toques:
   ```bash
   sudo systemctl status mysql --no-pager | head -3
   sudo ss -tlnp | grep 3306
   ```
4. Confirma que el puerto 5432 está libre:
   ```bash
   sudo ss -tlnp | grep 5432   # debe estar vacío
   ```
5. Snapshot defensivo de MySQL antes de tocar nada (por si acaso):
   ```bash
   mysqldump -u jpmarichal -p alejandria | gzip > /tmp/mysql-alejandria-$(date -u +%Y%m%dT%H%M%SZ).sql.gz
   ls -lh /tmp/mysql-alejandria-*.sql.gz
   ```
   Baja ese archivo a local si la paranoia pica. No instales Postgres hasta que este snapshot exista.

**Salta el paso 2 (hardening)** si el VPS ya tiene usuario no-root con sudo, UFW configurado y SSH endurecido — probablemente sí, dado que lleva MySQL en producción. Verifica sin modificar:

```bash
# Usuario actual con sudo
sudo -v && echo "sudo OK"

# SSH root deshabilitado
sudo grep -E '^PermitRootLogin' /etc/ssh/sshd_config

# UFW activo (si se usa)
sudo ufw status
```

Si algo no está, regresa al paso 2 del manual para aplicar lo que falte sin destruir config existente.

### 1.5 Swap de 4 GB (CRÍTICO en este VPS)

Con solo ~500 MB de RAM libre tras MariaDB, Postgres puede gatillar OOM-killer sin swap. Añade antes de continuar:

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Usar swap conservadoramente, no agresivamente
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.d/99-alejandria.conf

# Verificar
free -h             # Swap debe mostrar 4.0Gi
swapon --show
```

Si el VPS ya tiene swap suficiente (>= 2 GB), puedes saltar esta fase.

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
# --- Memoria (ajustado a COEXISTENCIA con MariaDB, no dedicado) ---
# Benchmark usaba shared_buffers=1GB en host dedicado.
# Aquí MariaDB ocupa ~3 GB de los 3.8 GB totales, así que recortamos.
shared_buffers = 512MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 256MB

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

**Impacto esperado del recorte de memoria:** queries FTS y semantic pueden ser 20-40 % más lentas vs el benchmark (que midió p95=44 ms FTS y p95=2.4 ms semantic). Queries KG simples (`kg_neighbors`, `kg_profile`) apenas se notan. Si en producción el p95 supera umbrales, considera upgrade a VPS L (8 GB) — ahí recuperamos `shared_buffers=1GB` con aire para MariaDB.

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

**Append** (no insertar con `sed -i /^host/ i\\...` — eso duplica reglas por cada línea `host` existente en el archivo). Añade al final con heredoc:

```bash
HBA=/etc/postgresql/16/main/pg_hba.conf
sudo cp "$HBA" "$HBA.backup-$(date -u +%Y%m%dT%H%M%SZ)"

sudo tee -a "$HBA" > /dev/null <<'EOF'

# Alejandria — laptop laboral (TLS obligatorio)
hostssl alejandria  alejandria_rw  163.116.231.24/32  scram-sha-256
hostssl alejandria  alejandria_ro  163.116.231.24/32  scram-sha-256
# TODO: añadir IP de la máquina personal cuando se use
# hostssl alejandria  alejandria_rw  <IP_PERSONAL>/32  scram-sha-256
EOF

sudo grep -n alejandria "$HBA"   # deben ser exactamente 2 líneas
sudo systemctl reload postgresql@16-main
```

> **Si por error quedaron duplicados** (p. ej. corriste un sed incorrecto antes), dedupe con:
> ```bash
> sudo awk '!seen[$0]++' "$HBA" | sudo tee "$HBA.tmp" > /dev/null
> sudo mv "$HBA.tmp" "$HBA"
> sudo chown postgres:postgres "$HBA"
> sudo chmod 640 "$HBA"
> sudo systemctl reload postgresql@16-main
> ```

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

### Opción B — Self-signed (sin dominio) — **ESTA ES LA QUE APLICA**

```bash
sudo mkdir -p /etc/postgresql/16/main/certs
cd /etc/postgresql/16/main/certs
sudo openssl req -new -x509 -days 730 -nodes -text \
  -out server.crt -keyout server.key \
  -subj "/CN=212.227.243.210"
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
# Estado actual de UFW (puede estar inactive o con reglas previas)
sudo ufw status

# Si UFW está inactive y lo vas a activar ahora: ABRE SSH PRIMERO para no cortarte tú mismo
sudo ufw allow 22/tcp comment 'SSH'

# Regla específica para Postgres desde tu laptop laboral
sudo ufw allow from 163.116.231.24 to any port 5432 proto tcp comment 'Alejandria laptop'
# TODO: la IP de la máquina personal se añade cuando se use
# sudo ufw allow from <IP_PERSONAL> to any port 5432 proto tcp comment 'Alejandria home'

# Activar si no estaba (con SSH ya permitido)
sudo ufw --force enable

# Estado final
sudo ufw status numbered
```

### IONOS Cloud Firewall (capa independiente)

IONOS expone un firewall adicional a nivel de consola cloud que es **independiente** de UFW. Si alguna de las dos capas bloquea, no entras:

1. Login https://cloud.ionos.com
2. **Compute Engine → Servers → tu VPS → Firewall Policies**
3. Si hay una policy asignada: añadir regla ingress para puerto 5432/tcp desde `163.116.231.24/32`.
4. Si no hay policy asignada: el firewall IONOS está en default-allow — UFW es la única barrera y ya está configurado.

Confirma antes de pasar al test que Postgres sigue corriendo:

```bash
sudo systemctl status postgresql@16-main --no-pager | head -5
```

Verificar desde dentro del VPS:

```bash
sudo -u postgres psql -c "SHOW ssl;"
# Debe devolver: on
```

## 9. Test de conexión remota (desde la máquina local)

Dos caminos equivalentes — usa el que prefieras:

### Opción A — psql en WSL (CLI)

```bash
# Instalar cliente en WSL Ubuntu-20.04 (ya lo usamos para GPU Docker)
wsl -d Ubuntu-20.04 sudo apt install -y postgresql-client-16

# Test de conectividad bruta (TCP)
wsl -d Ubuntu-20.04 bash -c "nc -zv 212.227.243.210 5432"
# Esperado: "Connection to 212.227.243.210 5432 port [tcp/postgresql] succeeded!"

# Conexión autenticada con TLS (sslmode=require = cifra pero no valida CA)
wsl -d Ubuntu-20.04 bash -c "PGPASSWORD='<password_rw>' psql \
  'host=212.227.243.210 port=5432 dbname=alejandria user=alejandria_rw sslmode=require' \
  -c 'SELECT version(); SELECT extname, extversion FROM pg_extension ORDER BY extname;'"
```

### Opción B — DBeaver (GUI)

Si tienes DBeaver instalado, más rápido de iterar:

1. **Database → New Database Connection → PostgreSQL**
2. Pestaña **Main**:
   - Host: `212.227.243.210`
   - Port: `5432`
   - Database: `alejandria`
   - Username: `alejandria_rw`
   - Password: `<del password manager>`
3. Pestaña **SSL**:
   - **Use SSL** ✓
   - **SSL mode**: `require` (no `verify-full`, el cert es self-signed)
   - Dejar los otros campos vacíos
4. **Test Connection**. Debe reportar éxito.
5. Una vez abierto, ejecutar: `SELECT version(); SELECT extname FROM pg_extension;`

Salida esperada en cualquiera de las dos opciones:
- PostgreSQL 16.13
- 4 extensiones: `plpgsql`, `pg_trgm`, `unaccent`, `vector`

Si falla con timeout o "connection refused", en orden:
1. `nc -zv 212.227.243.210 5432` — si falla aquí, es red (UFW, IONOS Cloud Firewall, o tu IP cambió).
2. `psql` con error de auth — es `pg_hba.conf` (verificar que tu IP pública actual coincide con la whitelist).
3. `psql` con error de SSL — certificado o config de `ssl = on` en postgres.

#### Caso especial: red corporativa bloquea outbound 5432

**Síntoma:** `Test-NetConnection 212.227.243.210 -Port 5432` y `nc -zv` **time out** desde la laptop, pero **`nc -zv 212.227.243.210 5432` succeeded desde el propio VPS**. UFW, IONOS Firewall y Postgres están bien — el firewall corporativo bloquea outbound en puertos no-estándar (permite 80/443/22).

**Solución: SSH tunnel sobre el 22** (que ya pasa por corporativo porque usas SSH normalmente).

##### Paso 1 — Habilitar pg_hba para loopback

El túnel SSH hace que las conexiones lleguen a Postgres con source IP `127.0.0.1`. El `pg_hba.conf` default de Ubuntu **ya tiene** `host all all 127.0.0.1/32 scram-sha-256` — verifica:

```bash
sudo grep "127.0.0.1" /etc/postgresql/16/main/pg_hba.conf
```

Si el resultado **no incluye** `alejandria`, añadir explícitamente:

```bash
sudo tee -a /etc/postgresql/16/main/pg_hba.conf > /dev/null <<'EOF'
# SSH tunnel — desde dentro del VPS, source es 127.0.0.1
host alejandria alejandria_rw 127.0.0.1/32 scram-sha-256
host alejandria alejandria_ro 127.0.0.1/32 scram-sha-256
EOF
sudo systemctl reload postgresql@16-main
```

##### Paso 2 — DBeaver con SSH tunnel (RUTA VERIFICADA 2026-04-18)

Configuración que funcionó:

| Pestaña | Campo | Valor |
|---|---|---|
| **SSH** | Use SSH Tunnel | ✓ |
| | Host/IP | `212.227.243.210` |
| | Port | `22` |
| | User Name | `root` |
| | Authentication Method | `Password` (también funciona `Public Key` si la tienes) |
| | Password | password SSH del root |
| | Save credentials | ✓ (opcional) |
| **General** | Host | `localhost` ← NO el IP público |
| | Port | `5432` |
| | Database | `alejandria` |
| | Username | `alejandria_rw` |
| | Password | password PWD_RW del password manager |
| **SSL** | SSL mode | `disable` ← el túnel SSH ya cifra; Postgres para 127.0.0.1 usa `host` no `hostssl` |

Test Connection debe mostrar "Conectado (~3000 ms)" primera vez, más rápido después. Server: `PostgreSQL 16.13 on x86_64-pc-linux-gnu`. Driver: `PostgreSQL JDBC Driver 42.7.2`.

##### Paso 3 — CLI equivalente para scripts/migradores

```bash
# Abre túnel en background (persiste hasta que mates el proceso).
# IMPORTANTE: bind a `*` (todas las interfaces) para que contenedores
# Docker en la red `bridge` por defecto alcancen el túnel vía
# host.docker.internal. Si solo necesitas acceso desde el shell host,
# usa `-L 15432:localhost:5432` (bind a 127.0.0.1).
ssh -L '*:15432:localhost:5432' -N -f root@212.227.243.210

# Verifica que el puerto está escuchando en todas las interfaces
# (debe aparecer 0.0.0.0:15432, no solo 127.0.0.1:15432)
ss -tlnp | grep 15432

# Ahora localhost:15432 = 212.227.243.210:5432 desde dentro del VPS
psql "host=localhost port=15432 dbname=alejandria user=alejandria_rw sslmode=disable"

# Cerrar túnel cuando termines
pkill -f "ssh.*15432"
```

##### Implicación para Fase 5 (migradores)

Correr migradores con el túnel activo:
```bash
ALEJANDRIA_POSTGRES_HOST=localhost
ALEJANDRIA_POSTGRES_PORT=15432
ALEJANDRIA_POSTGRES_SSLMODE=disable
ALEJANDRIA_POSTGRES_USER=alejandria_rw
ALEJANDRIA_POSTGRES_PASSWORD=<PWD_RW>
ALEJANDRIA_POSTGRES_DB=alejandria
```

Para Docker containers en WSL hay dos rutas:

- **`--network host`** en un `docker run` de una-sola-vez: el contenedor
  comparte la red del host, `localhost:15432` resuelve directo al túnel.
- **Red `bridge` por defecto** (como la usa `docker-compose.yml`): el
  contenedor no ve `localhost` del host. Apunta a
  `ALEJANDRIA_POSTGRES_HOST=host.docker.internal` y asegúrate de que el
  túnel esté bound a `0.0.0.0` (ver nota sobre `-L '*:...'` arriba).
  `docker-compose.yml` ya declara `extra_hosts: host.docker.internal:
  host-gateway` y el override correspondiente en `environment:`.

**Alternativas** (por si el túnel no escala):
- **Desde la máquina personal** (otra red, distinto ISP): conexión directa al 5432 probablemente funcione sin túnel.
- **Correr migradores en el propio VPS**: clonar el repo allá y ejecutar directo. Evita el túnel pero requiere subir 3.5 GB de SQLite (scp o similar).

Si esto funciona, **estás listo para aplicar el DDL desde la máquina local**.

## 10. Aplicar el DDL de Alejandría desde local

Desde el repo en la laptop:

```bash
# En Ubuntu-20.04 WSL (per feedback_docker_engine)
wsl -d Ubuntu-20.04 bash -c "docker run --rm \
  -v /mnt/c/own/alejandria:/app -w /app -e PYTHONPATH=/app/src \
  -e ALEJANDRIA_POSTGRES_HOST=212.227.243.210 \
  -e ALEJANDRIA_POSTGRES_PORT=5432 \
  -e ALEJANDRIA_POSTGRES_USER=alejandria_rw \
  -e ALEJANDRIA_POSTGRES_PASSWORD='<password_rw>' \
  -e ALEJANDRIA_POSTGRES_DB=alejandria \
  -e ALEJANDRIA_POSTGRES_SSLMODE=require \
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

## Rescue: root password recovery via IONOS panel

Cuando SSH no funciona (key no autorizada) y el password de consola no se reconoce:

1. **Cloud Panel** → Infrastructure > Server → clic en **DVD drive**
2. Activar **Gparted latest_iso** → **Load DVD** (server rebootea desde el DVD rescue)
3. **Action > Open remote console** → **Enter command line prompt** (opción 3, evita X11)
4. Identificar partición root: `lsblk` (típicamente `/dev/vda1`)
5. Montar y chroot:
   ```bash
   mount /dev/vda1 /mnt && chroot /mnt
   passwd root
   exit && sync && umount /mnt
   ```
6. **Eject DVD** y **Actions > Restart** desde el Cloud Panel
7. Autorizar llave SSH:
   ```bash
   # Si authorized_keys tiene atributos ia (immutable+append-only):
   chattr -ia /root/.ssh/authorized_keys
   echo "ssh-ed25519 AAAAC3..." >> /root/.ssh/authorized_keys
   ```

## SSH tunnel: desde Podman machine

Desde la migración a Podman Desktop, el túnel SSH a IONOS Postgres se inicia
**dentro del Podman machine** (`podman-machine-default`), no desde Windows/WSL.
Esto asegura que `host.containers.internal:15432` sea alcanzable desde los
contenedores (misma VM).

El script `scripts/gpu-podman.sh` maneja el túnel automáticamente en `up`:
```bash
bash scripts/gpu-podman.sh up
```

Si el túnel se cae, reiniciarlo manualmente:
```bash
MSYS_NO_PATHCONV=1 podman machine ssh podman-machine-default \
  "ssh -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes \
    -i ~/.ssh/id_ed25519 \
    -L '*:15432:localhost:5432' -N -f root@212.227.243.210"
```

## Referencias

- PGDG APT repo: https://wiki.postgresql.org/wiki/Apt
- pgvector: https://github.com/pgvector/pgvector
- Let's Encrypt para Postgres: https://www.postgresql.org/docs/current/ssl-tcp.html
- `postgresql.conf` tuning: https://pgtune.leopard.in.ua (introducir 4 GB + SSD + Web app)
