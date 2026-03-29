# P9 — Fine-Tuning — Requirements

## Problem Statement

The system uses general-purpose LLMs that have no domain-specific optimization for LDS scripture and gospel content. Fine-tuning or systematic prompt optimization could improve answer quality, reduce hallucination, and lower costs by enabling smaller models to perform well on domain-specific tasks.

## Functional Requirements

### FR-1: Evaluation Benchmark
A curated set of 100+ question-answer pairs covering:
- Factual questions ("Who baptized Jesus?")
- Analytical questions ("Compare the covenants of Abraham and Moses")
- Disambiguation questions ("Which Judas betrayed Jesus?")
- Bilingual questions (same questions in EN and ES)
- Edge cases (entities in both volumes, ambiguous names, doctrinal nuance)

### FR-2: Prompt Optimization
Systematic testing and optimization of:
- System prompts for RAG pipeline
- Entity profile generation prompts
- Query expansion prompts
- Reranking prompts

### FR-3: Embedding Model Evaluation
Compare the current embedding model against alternatives:
- Larger multilingual models
- Domain-fine-tuned embeddings (if available)
- Retrieval quality metrics (precision, recall, MRR)

### FR-4: LLM Fine-Tuning (Optional)
If evaluation shows significant quality gaps:
- Fine-tune a small model on the evaluation benchmark
- Compare against prompted general-purpose models
- Cost/quality tradeoff analysis

## Non-Functional Requirements

- Evaluation must be reproducible and automated
- Benchmark results must be version-tracked
- Changes to prompts must be A/B testable

## Dependencies

- None (can be done at any time, but benefits from stable features)

## Out of Scope

- Training custom embedding models from scratch
- Training custom LLMs from scratch
- Deployment of fine-tuned models (infrastructure concern)
