"""
OpenAI-only LLM client for prompt-based matching.
Uses Chat Completions with JSON mode enforced.

Env vars:
- OPENAI_API_KEY=...             # required
- OPENAI_MODEL=gpt-4o-mini       # optional (default below)
- OPENAI_TEMPERATURE=0.1         # optional
- OPENAI_MAX_TOKENS=1200         # optional
- LOG_LLM_USAGE=0|1              # optional; if 1, print token usage
"""

import os
from typing import Optional
from openai import OpenAI


def _get_client() -> OpenAI:
    """
    Create OpenAI client. Reads OPENAI_API_KEY from env.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    # You can also pass organization/project via env if you use multiple orgs:
    # OPENAI_ORG_ID / OPENAI_PROJECT
    return OpenAI(api_key=api_key)


def llm_complete(system: str, user: str) -> str:
    """
    Call Chat Completions with JSON mode so the model MUST return a single JSON object.

    Returns:
        str: JSON string (single object) from the model.

    Raises:
        RuntimeError: if OpenAI returns empty content or client is misconfigured.
        Exception:    bubble up API errors (caller wraps into HTTPException).
    """
    if not system or not user:
        raise RuntimeError("Both 'system' and 'user' messages must be non-empty")

    client = _get_client()
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "1200"))

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},  # enforce valid JSON
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Optional: log token usage for cost monitoring
    if os.getenv("LOG_LLM_USAGE", "0") == "1" and getattr(resp, "usage", None):
        try:
            u = resp.usage  # has prompt_tokens, completion_tokens, total_tokens
            print(f"[LLM usage] prompt={u.prompt_tokens} completion={u.completion_tokens} total={u.total_tokens}")
        except Exception:
            pass

    content: Optional[str] = resp.choices[0].message.content if resp.choices else None
    if not content:
        raise RuntimeError("OpenAI returned empty content")
    return content