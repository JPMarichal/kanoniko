# Reseñas

Directorio de reseñas producidas como parte del Paso 4 del workflow
de ingesta (`docs/ingestion-workflow.md` §4). Cada reseña es
**a la vez** un producto de cara al lector humano (catálogo SUD
publicable) y el depósito de metadata para los pasos técnicos de
ingestión (autoridad, KG pre-seed, paths, descarga).

## Estructura

```
prods/reseñas/
├── TEMPLATE.md            # plantilla canónica — copiar + renombrar
├── README.md              # este archivo
└── {slug}/
    ├── reseña.md          # el documento
    └── portada.jpg        # opcional, si la reseña se va a publicar
```

## Regla de 7 secciones humanas + 1 bloque IA

La plantilla define **7 secciones para el lector humano**, seguidas
por un bloque final con metadata IA delimitado por comentarios HTML:

```
<!-- ===== METADATA IA — NO PUBLICAR ===== -->
...
<!-- ===== FIN METADATA IA ===== -->
```

El bloque IA es *sólo* para el pipeline de ingestión. Scripts de
publicación del catálogo lo eliminan con una regex antes de exportar
a WordPress / web.

## Lifecycle vía el research backlog

Cada slug tiene una entrada en `backlogs/research.json`:

- `pendiente` → aún sin `reseña.md` en disco.
- `en_progreso` → documento creado pero incompleto.
- `completa` → documento completo con las 7 secciones humanas y el
  bloque IA. Hasta entonces los pasos 5 (autoridad), 6 (KG pre-seed)
  y 7 (formato) del workflow **no pueden empezar** — la reseña es el
  gate bloqueante (§4 del workflow).

El script `scripts/reconcile_backlogs.py` detecta cuándo
`prods/reseñas/{slug}/reseña.md` aparece en disco y propone mover el
status a `completa`.
