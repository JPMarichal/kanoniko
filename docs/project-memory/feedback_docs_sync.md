---
name: feedback_docs_sync
description: Mantener la documentación sincronizada con los cambios operativos en el MISMO turno, sin esperar a que el usuario lo pida
type: feedback
---

Regla del usuario (2026-04-18): cualquier ajuste que se aplique durante la ejecución de un procedimiento debe reflejarse en el doc correspondiente en el mismo mensaje donde se ejecuta la corrección. No esperar a recordatorio.

## Qué debe gatillar actualización inmediata

- Corrección a un comando porque falló o produjo resultados no deseados (p. ej. `sed -i "/^host/ i\\..."` que duplicó reglas → cambiar a append por heredoc).
- Descubrimiento que invalida supuestos del doc (OS real vs. asumido, servicios vecinos distintos, recursos reales disponibles).
- Cleanup o paso defensivo añadido ad-hoc (ej. `awk '!seen[$0]++'` para dedup).
- Numeración de fases que cambia porque se agregó una intermedia (ej. fase 1.5 swap).
- Valores personalizados (IPs, nombres de hosts, rutas) que antes eran placeholders.

## Antídoto operacional

Cuando aplique una corrección en vivo, en el MISMO turno debo:

1. Editar el doc con el cambio.
2. Commitear localmente (`git add docs/... && git commit -m "..."`).
3. Indicar en la respuesta al usuario que el doc quedó actualizado (breve).

No hacer push salvo que el usuario lo pida explícitamente — sigue la regla estándar de esta rama.

## Origen del feedback

Durante la Fase 0 de IONOS (postgres-migration) apliqué un `sed -i` frágil que duplicó reglas en `pg_hba.conf` 4 veces. Di el cleanup con `awk` pero no lo incorporé al doc inmediatamente; el usuario recordó la regla explícitamente.
