import diskcache
import hashlib
import json
import os
from textwrap import indent
from pathlib import Path
from typing import Any, Callable

from pydantic_core import ValidationError as CoreValidationError

from utils import logger

class ValidationError(Exception):
    "Our own model validation error type, representing the situation where the LLM's response can't be matched up with the supplied response_model"
    pass

def _log_llm_response(result):
    """
    Emit the LLM response at INFO level in a readable form.
    Accepts plain strings, Pydantic models or arbitrary objects.
    """
    try:
        if isinstance(result, str):
            payload = result
        elif hasattr(result, "model_dump_json"):      # pydantic-v2
            payload = result.model_dump_json()
        elif hasattr(result, "model_dump"):           # pydantic-v1
            payload = json.dumps(result.model_dump(), default=str)
        else:
            payload = str(result)
    except Exception as exc:                          # never let logging crash the flow
        payload = f"<unserialisable response: {exc!r}>"
    logger.debug("LLM response: %s", payload)

# Set up cache directory
cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.cache')
os.makedirs(cache_dir, exist_ok=True)
cache = diskcache.Cache(cache_dir)

def _generate_cache_key(provider, model_name, system_message, user_content, max_tokens, response_model):
    """Generate a unique cache key for the request parameters."""

    model_key = ":".join([provider, model_name])

    # Convert user_content to a stable string representation if it's a list
    if isinstance(user_content, list):
        def default_serializer(obj):
            if isinstance(obj, Path):
                return str(obj)
            return str(obj)
            
        content_str = json.dumps(user_content, sort_keys=True, default=default_serializer)
    else:
        content_str = str(user_content)
    
    # Include model class name as part of the key if response_model is provided
    model_class_name = response_model.__name__ if response_model else "none"
    
    key_parts = [model_key, system_message, content_str, str(max_tokens), model_class_name]
    combined = "||".join(key_parts)

    cache_key = hashlib.md5(combined.encode()).hexdigest()
    logger.info("Generated cache key: %s", cache_key)
    return cache_key

def _maybe_use_cached_result(cache_key: str, response_model, log_msg: str):
    """
    If *cache_key* is found, log, deserialize (when needed) and return it.
    Returns None when the key is absent so caller can continue with the live call.
    """
    cached_result = cache.get(cache_key)
    if cached_result is None:
        logger.info("Cache MISS for key %s", cache_key)
        return None
    logger.info(log_msg)
    _log_llm_response(cached_result)
    if response_model is None:
        return cached_result
    return response_model.model_validate_json(cached_result)

def _cache_and_return_result(result, cache_key: str, response_model):
    """
    Persist *result* to the global `cache` and return it unchanged.

    • When *response_model* is provided we store the JSON serialization
      (result.model_dump_json()) so `_maybe_use_cached_result()` can later
      rebuild the Pydantic instance.

    • Otherwise we store the raw result object (string / dict / etc.).
    """
    if response_model is not None:
        cache.set(cache_key, result.model_dump_json())
    else:
        cache.set(cache_key, result)
    logger.info("Stored new result in cache under key %s", cache_key)
    return result

def _invoke_with_cache(
    call_fn: Callable[[], Any],
    cache_key: str,
    response_model,
    cache_hit_msg: str,
):
    """
    Run *call_fn* only when the result is not already cached.
    Handles cache lookup, logging, call execution and persisting
    the new result in a single place.
    """
    hit = _maybe_use_cached_result(cache_key, response_model, cache_hit_msg)
    if hit is not None:
        return hit
    logger.info("Cache MISS – performing live LLM call …")

    result = call_fn()               # live LLM call
    _log_llm_response(result)
    return _cache_and_return_result(result, cache_key, response_model)

def _pretty_format_user_content(content) -> str:
    """Return a human-readable, multi-line string representation of user_content
    where long text fields are printed with real newlines instead of the escaped
    '\n' characters produced by json.dumps."""

    if not isinstance(content, list):
        return str(content)

    lines = []
    for idx, item in enumerate(content):
        # Typical Anthropic message items are dicts with {'type', 'text'}
        if isinstance(item, dict) and "text" in item:
            header = f"content[{idx}] ({item.get('type', 'text')}):"
            body   = indent(item["text"].rstrip(), "  ")
            lines.append(f"{header}\n{body}")
        else:
            # Fallback representation for non-dict items (e.g. PDF objects)
            lines.append(f"content[{idx}]: {item!r}")
    return "\n".join(lines)

def _log_request_details(model_name: str, system_message: str,
                         user_content: list | str, max_tokens: int,
                         temperature: float, provider: str):
    """
    Emit a single INFO entry summarising the outbound LLM request.
    This is called by both Anthropic and OpenAI wrappers so users
    always see: provider, model, token budget and a readable copy of
    the user-visible prompt content.
    """
    pretty_content = _pretty_format_user_content(user_content)
    logger.info(
        "LLM request [provider=%s | model=%s | max_tokens=%d | temp=%.2f]\n"
        "system: %s\n"
        "%s",
        provider, model_name, max_tokens, temperature,
        system_message or "<EMPTY>",
        pretty_content,
    )

def _load_provider(provider: str):
    provider = provider.lower()
    if provider in {"anthropic", "claude"}:
        from utils.llm_anthropic import cached_llm_invoke as invoke
    elif provider == "openai":
        from utils.llm_openai import cached_llm_invoke as invoke
    else:
        raise ValueError(f"Unknown provider '{provider}'")
    return invoke

def cached_llm_invoke(
        model_name: str | None = None,
        system_message: str = "",
        user_content: list = [],
        max_tokens: int = 2048,
        temperature: float = 0,
        response_model=None,
        provider: str = "anthropic",
):
    if model_name is None:
        model_name = os.environ.get("LLM_MODEL_NAME")

    logger.info("Dispatching call to %s provider (model=%s)",
                provider, model_name or "<default>")

    invoke = _load_provider(provider)
    try:
        response_model_instance = invoke(
            model_name=model_name,
            system_message=system_message,
            user_content=user_content,
            max_tokens=max_tokens,
            temperature=temperature,
            response_model=response_model,
        )
    except CoreValidationError as exc:
        msg = f"Validation error calling LLM: {str(exc)}"
        logger.error(msg)
        raise ValidationError(msg)

    return response_model_instance

__all__ = ["cached_llm_invoke", "ValidationError"]
