# ADR 0002 — Modular monolith (not microservices)

**Estado:** aprobado · **Fecha:** 2026-09-10 · **Contexto:** evaluación de
`docs/ARCHITECTURE_PLAN.md` (propuesta de split a microservicios) frente al estado real y el tamaño
del equipo.

## Contexto

`docs/ARCHITECTURE_PLAN.md` (mayo 2026) propone dividir el monolito (~15 000 líneas, paquete plano
`src/alejandria/`) en 10–14 repos de microservicios: `alejandria-storage`, `-search`,
`-embeddings`, `-knowledge`, `-ingestion`, `-chat`, `-gateway`, `-mcp`, `-core`, `-content`, más
front-ends (`-wordpress`, `-web`, `-mobile`, `-admin`). Argumenta complejidad cognitiva, bloqueos
entre módulos, escalabilidad todo-o-nada e innovación lenta.

Hechos del contexto:

- **Equipo = 1** (un único stakeholder), asistido por agentes (Claude Code).
- Carga real minúscula: 10–10 000 queries semánticas/día (`docs/vector-db-options.md`).
- Ya corre como ~2 contenedores (`alejandria-api`, `alejandria-ollama`) + Postgres en IONOS.
- El intento previo `workspace-migration` — una versión *más suave* de esto (4 paquetes
  `uv`/`hatch` en un solo repo) — **rompió el build y se abandonó**.
- Los dolores declarados por el usuario (velocidad de ingesta, ruido del KG, calidad RAG, ahorro de
  tokens, GPU, contenedores, corpus) **no** son "el monolito me bloquea".

## Decisión

**Alejandría es un monolito modular. `src/alejandria/` permanece como un único paquete y repo.**

Se extrae un componente a proceso/repo separado **solo con evidencia concreta**, y solo en las
costuras sancionadas abajo.

### Costuras de extracción sancionadas

| Componente | Cuándo | Forma |
|---|---|---|
| Front-ends `alejandria-web` / `-wordpress` / `-mobile` (P5) | Cuando se construyan | Repos aparte desde el día 1 — otro lenguaje, otra cadencia, cara al público. Consumen la API REST. |
| Worker GPU de ingesta/embeddings | Si el ciclo de vida diverge del API de forma incómoda | **Mismo repo**, proceso worker sobre cola o job programado. No es "microservicio". |
| `prods/` (contenido: Formas T, dossiers, discursos) | Baja prioridad | Repo de contenido eventual — patrón de cambio distinto al código. |

### Fronteras internas (enforcement)

Direcciones de import permitidas dentro de `src/alejandria/`:

```
interfaces  (api, cli, mcp_server)
    │  puede importar ↓
knowledge   (chat, knowledge)
    │  puede importar ↓
retrieval   (search, embeddings)
    │  puede importar ↓
foundation  (storage, ingestion, config, authority)
```

- Nada importa `api` / `cli` / `mcp_server`.
- `storage` no importa capas superiores.
- `search` / `embeddings` no importan `chat` / `knowledge` / `api`.

Se fuerza con **`import-linter`** (`lint-imports`), vía `just check-boundaries` y un paso
no-bloqueante del pre-commit. El contrato vive en `pyproject.toml` (`[tool.importlinter]`).

## Alternativas consideradas

- **Split a 10–14 repos de microservicios (`ARCHITECTURE_PLAN.md`).** Rechazada: el beneficio es
  organizacional (equipos independientes) y no aplica a un equipo de 1; añade coste de sistemas
  distribuidos sin retorno; el intento más suave ya fracasó; consumiría 12 meses de roadmap que
  compiten con P11/P12/WI-3 (valor visible). Los KPIs del plan (P95 −50 %, deploys ×10, MTTR −87 %)
  no son creíbles para este contexto — partir un servicio añade saltos, no acelera.
- **Monorepo con N paquetes `uv`/`hatch` sin fronteras forzadas.** Rechazada: es lo que se
  abandonó; sin enforcement el churn de imports reaparece.
- **Monolito sin fronteras declaradas.** Rechazada: no ataca la "complejidad cognitiva" real.

## Consecuencias

- `docs/ARCHITECTURE_PLAN.md` queda **archivado** (banner en el propio doc + `planning-index.md`).
  Revivirlo exige convertirlo en proyecto del incubador (`proj/Pxx-repo-split/`) con su `01-spec.md`
  y un trigger explícito (segundo dev full-time, o divergencia real de escala de un componente).
- `system-spec.md` §1 refleja esta decisión.
- Nueva dependencia de dev: `import-linter`. Nuevo recipe `just check-boundaries`. Nuevo paso 7 del
  pre-commit (warn).
- Revisión: cuando se cumpla un trigger, o anualmente.
