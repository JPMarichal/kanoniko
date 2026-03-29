# P5 — Chat Client UI — Project Plan

## Phases

### Phase 1 — Core Chat (3-5 days)
**Deliverables:**
- Minimal chat interface: input, answer display, source list
- Connects to `POST /chat` API
- Markdown rendering for answers

**Tasks:**
1. Select frontend framework and set up project
2. Build chat input component with send/loading states
3. Build answer display with markdown rendering
4. Build source list with scripture references
5. Basic responsive layout

### Phase 2 — Source & Entity Exploration (3-4 days)
**Deliverables:**
- Clickable source citations with passage context
- Entity profile sidebar/modal
- Graph context visualization (simple list or mini-graph)

**Tasks:**
1. Source detail panel (click reference → show full passage)
2. Entity profile panel (click entity → show profile summary, aliases)
3. Display graph context from API response
4. Navigation between entities

### Phase 3 — Conversation History (2-3 days)
**Deliverables:**
- Conversation persistence (localStorage/IndexedDB)
- Conversation list sidebar
- Resume and delete conversations

**Tasks:**
1. Persist messages in browser storage
2. Conversation list with titles (derived from first question)
3. Load/resume previous conversations
4. Export to markdown

### Phase 4 — Polish & Settings (2-3 days)
**Deliverables:**
- Language toggle (EN/ES)
- Model/tier selection UI
- Token count and cost display
- Mobile-responsive refinements
- Dark/light theme

**Tasks:**
1. Settings panel with language, tier, theme controls
2. Display model info and token counts per answer
3. Mobile layout optimization
4. Error handling and offline state

## Milestones

| Milestone | Deliverable | Estimate |
|-----------|------------|----------|
| M1 | Functional chat (ask → answer → sources) | Day 5 |
| M2 | Source and entity exploration | Day 9 |
| M3 | Conversation history | Day 12 |
| M4 | Polished, responsive, production-ready | Day 15 |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Framework choice regret | Low | Start simple; all major frameworks can do this |
| CORS issues with API | Low | Configure FastAPI CORS middleware |
| LLM latency feels slow in UI | Medium | Streaming responses (SSE) if supported |

## Dependencies

- None (consumes existing REST API)

## Success Criteria

1. User can ask questions and receive grounded answers with clickable citations
2. Entity profiles accessible from within the chat
3. Conversation history persists across browser sessions
4. Works on mobile and desktop
