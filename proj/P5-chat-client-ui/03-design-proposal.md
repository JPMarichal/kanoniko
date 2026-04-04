# P5 — Chat Client UI — Design Proposal

## Stack

- **React + Vite + Tailwind** — ecosistema maduro, build rápido, dark/light trivial
- Contenedor propio en docker-compose (puerto 4301, proxy a API en 4300)
- Alternativa: archivos estáticos servidos por FastAPI (un solo contenedor)

## Layout: Tres paneles

```
┌──────────────┬────────────────────────────┬──────────────┐
│ Conversaciones│       Chat principal       │  Panel lateral│
│              │                            │  (contextual) │
│ - Lista      │  Pregunta del usuario      │              │
│ - Buscar     │  ┌─────────────────────┐   │  Fuentes     │
│ - Nueva conv │  │ Respuesta con FCD   │   │  ─ o ─       │
│              │  │ inline + refs       │   │  Perfil de   │
│              │  └─────────────────────┘   │  entidad     │
│              │                            │  ─ o ─       │
│              │  [────────────── Enviar]   │  Grafo mini  │
└──────────────┴────────────────────────────┴──────────────┘
```

- **Panel izquierdo:** historial de conversaciones (IndexedDB), colapsable en móvil
- **Panel central:** chat con markdown renderizado, citas FCD inline como `<Citation>` clicables
- **Panel derecho:** contextual — cambia según lo que el usuario cliquee:
  - Clic en cita → **Source Explorer** (pasaje en contexto, versículos alrededor)
  - Clic en entidad → **Entity Profile** (resumen, aliases, relaciones, menciones)
  - Default → **Graph Mini** (entidades mencionadas en la respuesta + sus conexiones)

## Interacciones clave

1. **Streaming** — SSE desde `/chat` para respuesta progresiva (latencia LLM 5-15s)
2. **Citas clicables** — parser detecta patrones FCD y los convierte en `<Citation>` que abren Source Explorer
3. **Entity chips** — entidades mencionadas aparecen como chips clicables debajo del mensaje
4. **Idioma automático** — detecta idioma de la pregunta; toggle manual en header
5. **Tier selector** — Rápido (Haiku), Balanceado (Sonnet), Profundo (Opus) con estimación de costo

## Componentes principales

| Componente | Función |
|------------|---------|
| `ChatInput` | Textarea + enviar, autosize, Ctrl+Enter |
| `ChatMessage` | Markdown renderer + citation parser + entity chips |
| `SourceExplorer` | Pasaje + contexto + navegación prev/next chapter |
| `EntityProfile` | Perfil + alias + relaciones (desde `kg_profile`) |
| `GraphMini` | Visualización simple de nodos/edges (d3-force o vis.js) |
| `ConversationList` | IndexedDB + títulos derivados de primera pregunta |
| `SettingsBar` | Idioma, tier, tema oscuro/claro |

## Decisiones de diseño

- **No server-side sessions** — todo en IndexedDB, zero auth
- **No GraphQL** — API REST suficiente
- **No SSR** — SPA pura, no necesita SEO
- **No graph complejo** — mini-graph decorativo/exploratorio

## Decisión pendiente

¿Cuarto contenedor en docker-compose o archivos estáticos servidos por FastAPI?
