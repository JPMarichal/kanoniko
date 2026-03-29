# P5 — Chat Client UI — Requirements

## Problem Statement

Alejandria's knowledge engine is fully functional via REST API, but has no user-facing interface. The final product vision is a specialized chat client for scripture/gospel study — an interactive UI that leverages all search modes, entity profiles, and RAG capabilities.

## Functional Requirements

### FR-1: Chat Interface
- Conversational UI with message history
- User types a question, receives a grounded answer with source citations
- Sources displayed as clickable references (scripture references, document links)
- Graph context visualized (entities mentioned, relationships)

### FR-2: Source Explorer
- Click a source citation to see the full passage in context
- Navigate to surrounding verses/paragraphs
- See other search results related to the same topic

### FR-3: Entity Explorer
- Click an entity name to see its profile (summary, aliases, mentions, books)
- Visualize entity connections from the knowledge graph
- Browse disambiguated variants (e.g., the 7 Judas individuals)

### FR-4: Bilingual Support
- UI language follows the question language (auto-detect)
- Toggle between English and Spanish answers
- Entity summaries shown in the appropriate language

### FR-5: Model Selection
- Display which model/tier was used for the answer
- Allow manual tier override (fast/balanced/quality)
- Show token counts and approximate cost

### FR-6: Conversation History
- Persist conversation threads
- Resume previous conversations
- Export conversation as markdown

## Non-Functional Requirements

- **Responsive**: Works on desktop and mobile browsers
- **Performance**: Answer appears within 3-10 seconds (dependent on LLM)
- **Accessibility**: Keyboard navigation, screen reader compatible
- **Offline-aware**: Graceful degradation when API is unavailable

## Technical Decisions (To Be Made)

- Frontend framework: React, Vue, Svelte, or other
- Hosting: same Docker Compose or separate service
- State management: local storage, IndexedDB, or server-side sessions

## Dependencies

- None (consumes existing REST API)

## Out of Scope

- User authentication and multi-tenancy
- Collaborative features (shared conversations)
- Native mobile app (web-responsive is sufficient for now)
