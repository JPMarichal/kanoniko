"""LLM provider abstraction — supports Anthropic, Google Gemini, and OpenAI-compatible APIs."""

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


def complete(system_prompt: str, user_message: str) -> LLMResponse:
    """Send a chat completion request to the configured LLM provider."""
    provider = settings.llm_provider.lower()
    if provider == "anthropic":
        return _complete_anthropic(system_prompt, user_message)
    elif provider == "gemini":
        return _complete_gemini(system_prompt, user_message)
    elif provider == "openai":
        return _complete_openai(system_prompt, user_message)
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. "
            "Use 'anthropic', 'gemini', or 'openai'."
        )


def _complete_anthropic(system_prompt: str, user_message: str) -> LLMResponse:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.llm_api_key or None)
    response = client.messages.create(
        model=settings.llm_model,
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


def _complete_gemini(system_prompt: str, user_message: str) -> LLMResponse:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.llm_api_key or None)
    response = client.models.generate_content(
        model=settings.llm_model,
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
        model=settings.llm_model,
        input_tokens=usage.prompt_token_count if usage else 0,
        output_tokens=usage.candidates_token_count if usage else 0,
    )


def _complete_openai(system_prompt: str, user_message: str) -> LLMResponse:
    from openai import OpenAI

    kwargs = {}
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    client = OpenAI(api_key=settings.llm_api_key or None, **kwargs)
    response = client.chat.completions.create(
        model=settings.llm_model,
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
