---
name: Alejandría - Chat Client Vision
description: Final MVP goal is a specialized chat client for scripture/gospel study, built on top of the knowledge engine
type: project
---

The ultimate goal of Alejandría is to become a **specialized chat client** for studying the scriptures and the gospel of Jesus Christ and His Church — similar to ChatGPT/Gemini but focused on the LDS corpus.

**Architecture implications:**
- The three search modes (textual, semantic, KG) are the **knowledge engine** (backend)
- The chat will be a separate service/frontend that does **RAG** over the knowledge engine's REST API
- Must be designed for growth: new capabilities added after MVP

**Post-MVP features to anticipate:**
- Conversation history and user profiles
- Personalized study plans
- Cross-references between scriptures
- Thematic concordance
- Bookmarks/notes/favorites
- Multi-turn context-aware dialogue

**Why:** User envisions this as a chat product, not just a search tool. Everything built must serve this end goal.

**How to apply:** Keep search API responses rich enough for RAG (full chunks, source citations, scripture references). Maintain clean service separation so the chat layer can be added independently. Design data models to be extensible.
