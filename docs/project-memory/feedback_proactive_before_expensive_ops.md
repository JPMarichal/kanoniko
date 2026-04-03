---
name: Revisar y optimizar antes de lanzar operaciones costosas
description: Antes de cualquier operación larga o difícil de revertir, verificar deuda técnica conocida y optimizar primero
type: feedback
---

Antes de lanzar cualquier operación costosa (reindex, full scan, migración, deploy), hacer un stop obligatorio:

1. ¿Hay deuda técnica conocida que hace esta operación más cara de lo necesario?
2. ¿El código actual refleja lo que ya sabemos sobre el problema?
3. ¿Existe un camino más rápido o seguro que no estamos tomando?

**Why:** En 2026-04-03 estuvimos a punto de lanzar un reindex con Phase 1 single-threaded, SHA scan de 24K archivos, y 2 conexiones SQLite por archivo — sabiendo que existían esas ineficiencias. Resultado evitado: 5h de Phase 1. Resultado real después de optimizar: 30 min (10x más rápido).

**How to apply:** Aplica a reindex, commits grandes, operaciones de base de datos, deployments, y cualquier cosa que tarde horas o sea difícil de revertir. El costo de pausar 20 minutos a revisar es trivial comparado con horas perdidas o un sistema en estado inconsistente. No lanzar hasta estar seguro de que el camino está despejado y optimizado.
