# LLM Models & Tiered Selection

Multi-provider LLM support with automatic tier-based model routing.

## Providers

| Provider | Models | API Key Variable |
|----------|--------|-----------------|
| **Anthropic** | Claude Haiku 4.5, Sonnet 4.5 | `ALEJANDRIA_LLM_ANTHROPIC_API_KEY` |
| **Google Gemini** | Gemini 2.5 Flash, Flash Lite | `ALEJANDRIA_LLM_GEMINI_API_KEY` |
| **OpenAI** | GPT-4o-mini | `ALEJANDRIA_LLM_OPENAI_API_KEY` |
| **DeepSeek** | DeepSeek Chat | `ALEJANDRIA_LLM_DEEPSEEK_API_KEY` |

Multiple providers can be configured simultaneously. The system selects the best available model per tier.

## Tier System

| Tier | Purpose | Typical Model | Cost (approx) |
|------|---------|--------------|----------------|
| **fast** | Internal calls, simple lookups | Gemini Flash Lite, DeepSeek | $0.07-0.30/1M tokens |
| **balanced** | Standard questions | Gemini 2.5 Flash | $0.30-2.50/1M tokens |
| **quality** | Complex analysis | Claude Sonnet/Haiku, GPT-4o-mini | $0.27-5.00/1M tokens |

## Automatic Complexity Classification

When `llm_answer_tier = "auto"`, the system classifies each question:

- **Fast**: Simple factual lookups ("What verse says...?", "Where is...?")
- **Balanced**: Standard questions requiring synthesis
- **Quality**: Complex analysis, comparisons, multi-entity questions

Classification uses keyword heuristics and question structure analysis.

## Per-Request Override

The chat API supports overriding provider, model, or tier per request:

```json
POST /chat
{
  "question": "...",
  "provider": "anthropic",
  "model": "claude-sonnet-4-5-20250514",
  "tier": "quality"
}
```

## Model Registry

Models are defined in `chat/models.py` as `ModelDef` dataclasses:
```python
ModelDef(
    id="gemini-2.5-flash-lite",
    provider="gemini",
    model_name="gemini-2.5-flash-lite",
    tier=Tier.FAST,
    cost_input=0.075,
    cost_output=0.30,
)
```

## Key Functions

- `classify_complexity(question)` → `Tier`
- `select_model(tier, provider)` → `ModelDef | None`
- `get_api_key(provider)` → `str`
- `get_available_models()` → `list[ModelDef]`

## A/B Comparison

`POST /chat/compare` runs the same question through two providers and returns both answers with token counts and cost estimates.
