import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / '.env')

DEFAULT_MODEL = os.getenv('GEMMA_MODEL', 'gemma-4-26b-a4b-it')
DEFAULT_THINKING_LEVEL = os.getenv('GEMMA_THINKING_LEVEL', '').strip() or None


def require_api_key() -> str:
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise RuntimeError(
            'Missing GEMINI_API_KEY. Copy .env.example to .env and fill in your key, '
            'or set GEMINI_API_KEY in your terminal before running.'
        )
    return api_key


def build_client():
    from google import genai

    api_key = require_api_key()
    return genai.Client(api_key=api_key)


def build_generation_config(
    *,
    max_output_tokens: int = 256,
    temperature: float | None = 0.0,
    top_p: float | None = None,
    top_k: int | None = None,
    thinking_level: str | None = None,
    seed: int | None = None,
):
    from google.genai import types

    config_kwargs: dict[str, Any] = {
        'max_output_tokens': max_output_tokens,
        'response_mime_type': 'text/plain',
    }
    if temperature is not None:
        config_kwargs['temperature'] = temperature
    if top_p is not None:
        config_kwargs['top_p'] = top_p
    if top_k is not None:
        config_kwargs['top_k'] = top_k
    if seed is not None:
        config_kwargs['seed'] = seed

    level = thinking_level or DEFAULT_THINKING_LEVEL
    if level:
        config_kwargs['thinking_config'] = types.ThinkingConfig(thinking_level=level)

    return types.GenerateContentConfig(**config_kwargs)


def _response_text_fallback(response: Any) -> str:
    candidates = getattr(response, 'candidates', None) or []
    text_parts: list[str] = []
    for candidate in candidates:
        content = getattr(candidate, 'content', None)
        parts = getattr(content, 'parts', None) or []
        for part in parts:
            text = getattr(part, 'text', None)
            if text:
                text_parts.append(text)
    return ''.join(text_parts).strip()


def extract_response_text(response: Any) -> str:
    text = getattr(response, 'text', None)
    if isinstance(text, str) and text.strip():
        return text.strip()
    return _response_text_fallback(response)


def extract_usage_metadata(response: Any) -> dict[str, Any] | None:
    usage = getattr(response, 'usage_metadata', None)
    if usage is None:
        return None
    fields = [
        'prompt_token_count',
        'candidates_token_count',
        'total_token_count',
        'thoughts_token_count',
        'cached_content_token_count',
    ]
    data: dict[str, Any] = {}
    for field in fields:
        value = getattr(usage, field, None)
        if value is not None:
            data[field] = value
    return data or None


def extract_finish_reason(response: Any) -> str | None:
    candidates = getattr(response, 'candidates', None) or []
    if not candidates:
        return None
    reason = getattr(candidates[0], 'finish_reason', None)
    if reason is None:
        return None
    return str(reason)


def generate_text(
    client,
    *,
    model: str,
    prompt: str,
    config,
    retries: int = 3,
    retry_sleep: float = 2.0,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            return {
                'response_text': extract_response_text(response),
                'usage': extract_usage_metadata(response),
                'finish_reason': extract_finish_reason(response),
                'raw_error': None,
            }
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retries:
                time.sleep(retry_sleep * attempt)
                continue
    assert last_error is not None
    return {
        'response_text': '',
        'usage': None,
        'finish_reason': None,
        'raw_error': f'{type(last_error).__name__}: {last_error}',
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
