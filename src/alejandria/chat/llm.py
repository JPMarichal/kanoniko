"""LLM provider abstraction — supports Anthropic, Google Gemini, and OpenAI-compatible APIs.

Functions accept explicit provider/model/api_key parameters to support the tiered
model selection system. When not provided, they fall back to global settings.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from alejandria.config import settings

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int


def complete(
    system_prompt: str,
    user_message: str,
    *,
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> LLMResponse:
    """Send a chat completion request to an LLM provider.

    Args:
        system_prompt: System instruction for the model.
        user_message: User message content.
        provider: LLM provider ("anthropic", "gemini", "openai").
                  Defaults to settings.llm_provider.
        model: Model name/ID. Defaults to settings.llm_model.
        api_key: API key. Defaults to settings.llm_api_key.
    """
    p = (provider or settings.llm_provider).lower()
    m = model or settings.llm_model
    k = api_key or settings.llm_api_key

    if p == "anthropic":
        return _complete_anthropic(system_prompt, user_message, m, k)
    elif p == "gemini":
        return _complete_gemini(system_prompt, user_message, m, k)
    elif p == "openai":
        return _complete_openai(system_prompt, user_message, m, k)
    elif p == "deepseek":
        return _complete_openai_compat(
            system_prompt, user_message, m, k,
            base_url="https://api.deepseek.com",
        )
    else:
        raise ValueError(
            f"Unknown LLM provider: {p}. "
            "Use 'anthropic', 'gemini', 'openai', or 'deepseek'."
        )


def complete_with_model(
    system_prompt: str,
    user_message: str,
    model_def: "ModelDef",  # noqa: F821 — forward ref to avoid circular import
) -> LLMResponse:
    """Send a completion request using a ModelDef from the model registry.

    This is the preferred entry point for tiered model selection.
    """
    from alejandria.chat.models import get_api_key

    key = get_api_key(model_def.provider)
    if not key:
        raise ValueError(f"No API key configured for provider '{model_def.provider}'")

    return complete(
        system_prompt,
        user_message,
        provider=model_def.provider,
        model=model_def.model_name,
        api_key=key,
    )


def _complete_anthropic(system_prompt: str, user_message: str, model: str, api_key: str) -> LLMResponse:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key or None)
    response = client.messages.create(
        model=model,
        max_tokens=settings.llm_max_tokens,
        temperature=settings.llm_temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return LLMResponse(
        text=response.content[0].text,
        model=response.model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


def _complete_gemini(system_prompt: str, user_message: str, model: str, api_key: str) -> LLMResponse:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key or None)
    response = client.models.generate_content(
        model=model,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
        ),
    )
    usage = response.usage_metadata
    return LLMResponse(
        text=response.text,
        model=model,
        input_tokens=usage.prompt_token_count if usage else 0,
        output_tokens=usage.candidates_token_count if usage else 0,
    )


def _complete_openai_compat(
    system_prompt: str, user_message: str, model: str, api_key: str,
    *, base_url: str,
) -> LLMResponse:
    """Generic completion for any OpenAI-compatible API (DeepSeek, Groq, Together, etc.)."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        max_tokens=settings.llm_max_tokens,
        temperature=settings.llm_temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    choice = response.choices[0]
    usage = response.usage
    return LLMResponse(
        text=choice.message.content,
        model=response.model,
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
    )


def _complete_openai(system_prompt: str, user_message: str, model: str, api_key: str) -> LLMResponse:
    from openai import OpenAI

    kwargs = {}
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    client = OpenAI(api_key=api_key or None, **kwargs)
    response = client.chat.completions.create(
        model=model,
        max_tokens=settings.llm_max_tokens,
        temperature=settings.llm_temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    choice = response.choices[0]
    usage = response.usage
    return LLMResponse(
        text=choice.message.content,
        model=response.model,
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
    )
