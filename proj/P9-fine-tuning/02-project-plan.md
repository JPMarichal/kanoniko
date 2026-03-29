# P9 — Fine-Tuning — Project Plan

## Phases

### Phase 1 — Evaluation Benchmark (3-4 days)
**Deliverables:**
- 100+ curated Q&A pairs in JSON format
- Automated evaluation script
- Baseline scores for current system

**Tasks:**
1. Create question categories and difficulty levels
2. Write Q&A pairs covering all categories (EN/ES)
3. Build evaluation runner: question → system answer → compare with reference
4. Metrics: accuracy, relevance, citation correctness, bilingual consistency
5. Run baseline evaluation and document scores

### Phase 2 — Prompt Optimization (3-5 days)
**Deliverables:**
- Optimized system prompts for all LLM calls
- A/B comparison results
- Documented prompt versions with scores

**Tasks:**
1. Identify lowest-scoring question categories
2. Iterate on system prompt for RAG answers
3. Iterate on profile generation prompt
4. Iterate on query expansion prompt
5. A/B test each change against baseline
6. Document winning prompts with rationale

### Phase 3 — Embedding Evaluation (2-3 days)
**Deliverables:**
- Retrieval quality comparison across 3+ embedding models
- Recommendation for optimal model
- Cost/performance tradeoff analysis

**Tasks:**
1. Select candidate embedding models
2. Index a subset of corpus with each model
3. Run retrieval benchmark (query → top-k → precision/recall/MRR)
4. Compare against current model
5. Recommend and document findings

### Phase 4 — Fine-Tuning (if justified) (5-7 days)
**Deliverables:**
- Fine-tuned model on domain data
- Comparison against prompted general-purpose models
- Deployment recommendation

**Tasks:**
1. Prepare training data from evaluation benchmark + corpus
2. Fine-tune candidate small model
3. Evaluate on benchmark
4. Compare cost/quality vs. prompted models
5. Decision: adopt or stay with prompted approach

## Milestones

| Milestone | Deliverable | Estimate |
|-----------|------------|----------|
| M1 | Benchmark complete, baseline scores | Day 4 |
| M2 | Prompts optimized, scores improved | Day 9 |
| M3 | Embedding evaluation complete | Day 12 |
| M4 | Fine-tuning decision made | Day 19 (if pursued) |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Benchmark bias toward current system | Medium | Include adversarial/edge-case questions |
| Fine-tuning doesn't justify cost | Low | Phase 4 is optional; prompted models may be sufficient |
| Embedding model change requires full re-index | High | Only change if improvement is substantial |

## Success Criteria

1. Evaluation benchmark reproducible and automated
2. Prompt optimization improves accuracy by measurable margin
3. Clear recommendation on embedding model with data backing
