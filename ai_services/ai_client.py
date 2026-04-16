"""
LLM API client wrapper — supports multiple free providers.
Supports: Groq (free), Grok/xAI, OpenAI, and any OpenAI-compatible API.
Centralises all LLM calls so the rest of the codebase stays LLM-agnostic.
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

_client = None
_provider = None


def _detect_provider() -> str:
    """Auto-detect which LLM provider is configured based on env vars."""
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    if os.getenv("GROK_API_KEY"):
        return "grok"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    raise EnvironmentError(
        "No LLM API key found. Set one of: GROQ_API_KEY, GROK_API_KEY, or OPENAI_API_KEY in .env"
    )


def _get_client():
    """Lazy-initialise and cache the LLM client."""
    global _client, _provider

    if _client is not None:
        return _client

    _provider = _detect_provider()

    if _provider == "groq":
        from groq import Groq
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    elif _provider == "grok":
        from openai import OpenAI
        _client = OpenAI(
            api_key=os.getenv("GROK_API_KEY"),
            base_url="https://api.x.ai/v1",
        )
    else:  # openai
        from openai import OpenAI
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    return _client


def get_model() -> str:
    """Return the configured model name based on provider."""
    global _provider
    if _provider is None:
        _provider = _detect_provider()

    defaults = {
        "groq": "llama-3.3-70b-versatile",
        "grok": "grok-3-mini-fast",
        "openai": "gpt-4o-mini",
    }
    env_key = f"{_provider.upper()}_MODEL"
    return os.getenv(env_key, defaults.get(_provider, "llama-3.3-70b-versatile"))


def ask_llm(prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
    """
    Send a prompt to the LLM and return the assistant's text reply.
    Raises on API errors so the caller can show a user-friendly message.
    """
    client = _get_client()
    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": "You are an expert educational assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def ask_llm_json(prompt: str, temperature: float = 0.4, max_tokens: int = 2500) -> list | dict:
    """
    Send a prompt to the LLM expecting a JSON response.
    Attempts to parse the response; falls back to returning raw text on failure.
    """
    raw = ask_llm(prompt, temperature=temperature, max_tokens=max_tokens)

    # Strip markdown code fences if the LLM wraps the JSON
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last lines (the fences)
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Return raw text so caller can handle gracefully
        return cleaned
