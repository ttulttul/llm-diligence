from pathlib import Path
from typing import Any
import os, json, base64, mimetypes
try:
    import magic                        # file-type detection via libmagic
except Exception:
    magic = None                        # gracefully degrade when libmagic is unavailable

from anthropic import Anthropic
from pydantic import BaseModel

from utils import logger               # local project logger
from utils.llm import (                # shared helpers
    _generate_cache_key,
    _invoke_with_cache,
    _log_request_details,
    _log_llm_response,
    ValidationError as LLMValidationError,
)

def format_content_for_anthropic(content):
    """Format content properly for the Anthropic API."""
    if isinstance(content, list):
        # For test compatibility, if it's a list of strings, join them with newlines
        if all(isinstance(item, str) for item in content):
            return [{"type": "text", "text": "\n".join(content)}]
        
        formatted_content = []
        for item in content:
            if isinstance(item, str):
                formatted_content.append({"type": "text", "text": item})
            elif isinstance(item, dict) and "type" in item and "text" in item:
                formatted_content.append(item)
            elif isinstance(item, Path):
                # Detect MIME type (prefer python-magic, fall back to file extension)
                mime_type = None
                if magic is not None:
                    try:
                        mime_type = magic.from_file(str(item), mime=True)
                    except Exception:
                        mime_type = None
                if mime_type is None:
                    mime_type, _ = mimetypes.guess_type(item.name)

                if mime_type == "application/pdf":
                    file_data = base64.standard_b64encode(item.read_bytes()).decode("utf-8")
                    formatted_content.append({
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": file_data,
                        },
                    })
                else:
                    # Fallback: read file as UTF-8 text (best-effort) and pass as a text part
                    try:
                        text_data = item.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        text_data = str(item)
                    formatted_content.append({"type": "text", "text": text_data})
            else:
                raise ValueError("Item is not a Path, dict, or str")
        logger.debug("Anthropic formatted_content: %s", formatted_content)
        return formatted_content
    else:
        logger.debug("Anthropic formatted_content (text): %s", content)
        return [{"type": "text", "text": content}]

def cached_llm_invoke(
    model_name: str | None = None,
    system_message: str = "",
    user_content: list = [],
    max_tokens: int = 2048,
    temperature: float = 0,
    response_model=None,
):
    """Anthropic/Claude implementation (code formerly in cached_llm_invoke)."""
    # Normalize optional parameters ------------------------------------------------
    if max_tokens is None:
        # Anthropic expects a positive integer – default to 2048 if caller passed None
        max_tokens = 2048
    if temperature is None:
        # Avoid TypeError inside the SDK when multiplying by ``None``
        temperature = 0
    # Get the Anthropic API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    _log_request_details(model_name, system_message, user_content,
                         max_tokens, temperature, provider="anthropic")

    # Use a safe string (empty) when model_name is None so list-joins inside
    # _generate_cache_key never receive a None value.
    cache_key = _generate_cache_key(
        "anthropic",
        model_name or "",
        system_message,
        user_content,
        max_tokens,
        response_model,
    )

    def _do_call():
        anthropic_client = Anthropic(api_key=api_key)
        formatted_content = format_content_for_anthropic(user_content)
        logger.debug("Anthropic request payload: model=%s, system=%s, messages=%s",
                     model_name or "claude-sonnet-4-20250514",
                     system_message,
                     formatted_content)
        # The new Anthropic SDK (≥0.20) exposes a `messages` endpoint instead of
        # the old `chat.completions` one.  Use it if available.
        raw_resp = anthropic_client.messages.create(
            model=model_name or "claude-sonnet-4-20250514",
            system=system_message,
            messages=[{"role": "user", "content": formatted_content}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        logger.debug("Raw Anthropic response: %s", raw_resp)
        # Extract JSON string returned by Claude
        content_json = (
            raw_resp.content[0].text             # typical Claude reply (list item)
            if hasattr(raw_resp, "content") else raw_resp
        )
        try:
            raw_dict = json.loads(content_json)
        except json.JSONDecodeError as e:
            # Wrap malformed JSON errors in our common validation error type
            logger.error("Invalid JSON received from Anthropic: %s", e)
            raise LLMValidationError(f"Invalid JSON from Anthropic model: {e}") from e

        from utils.llm import warn_on_empty_or_missing_fields
        warn_on_empty_or_missing_fields(raw_dict, response_model)

        validated = response_model.model_validate(raw_dict) if response_model else raw_dict
        return validated

    return _invoke_with_cache(
        _do_call, cache_key, response_model,
        "cached_llm_invoke: using cached result"
    )
