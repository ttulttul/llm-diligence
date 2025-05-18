# Standard library
import hashlib
import json
import os
from unittest.mock import MagicMock

# Third-party
import diskcache
import instructor
from anthropic import Anthropic
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from instructor.multimodal import PDF          # NEW
except ImportError:                                # NEW
    PDF = None                                     # NEW

from typing import Any, Callable

# Local
from utils import logger

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

def get_claude_model_name():
    """Get the Claude model name from environment variable or use default."""
    return os.environ.get("CLAUDE_MODEL_NAME", "claude-3-7-sonnet-20250219")

# Set up cache directory
cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.cache')
os.makedirs(cache_dir, exist_ok=True)
cache = diskcache.Cache(cache_dir)

def _generate_cache_key(model_name, system_message, user_content, max_tokens, response_model):
    """Generate a unique cache key for the request parameters."""
    # Convert user_content to a stable string representation if it's a list
    if isinstance(user_content, list):
        # Use a custom default function to handle PosixPath objects
        def default_serializer(obj):
            import pathlib
            if isinstance(obj, pathlib.Path):
                return str(obj)
            return str(obj)
            
        content_str = json.dumps(user_content, sort_keys=True, default=default_serializer)
    else:
        content_str = str(user_content)
    
    # Include model class name as part of the key if response_model is provided
    model_class_name = response_model.__name__ if response_model else "none"
    
    key_parts = [model_name, system_message, content_str, str(max_tokens), model_class_name]
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

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    # This is a stub function for testing
    # In a real implementation, this would use a PDF parsing library
    return f"Extracted text from {pdf_path}"

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
                # Already formatted content
                formatted_content.append(item)
            elif PDF is not None and isinstance(item, PDF):        # NEW – preserve PDF
                formatted_content.append(item)                     # NEW
            else:
                # Try to convert to string if not already formatted
                formatted_content.append({"type": "text", "text": str(item)})
        return formatted_content
    elif isinstance(content, str) and content.lower().endswith('.pdf'):
        # Handle PDF files by extracting text
        extracted_text = extract_text_from_pdf(content)
        return [{"type": "text", "text": extracted_text}]
    else:
        # Simple text content
        return [{"type": "text", "text": content}]

def _pretty_format_user_content(content) -> str:
    """Return a human-readable, multi-line string representation of user_content
    where long text fields are printed with real newlines instead of the escaped
    '\n' characters produced by json.dumps."""
    from textwrap import indent

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

# --------------------------------------------------------------------------- #
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

def _cached_claude_invoke(
    model_name: str | None = None,
    system_message: str = "",
    user_content: list = [],
    max_tokens: int = 2048,
    temperature: float = 0,
    response_model=None,
):
    """Anthropic/Claude implementation (code formerly in cached_llm_invoke)."""
    # --- original body of cached_llm_invoke START ---
    # Get the Anthropic API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    # If model_name is None, set it automatically to the default
    if model_name is None:
        model_name = get_claude_model_name()

    _log_request_details(model_name, system_message, user_content,
                         max_tokens, temperature, provider="anthropic")

    # Generate a cache key for this specific request
    cache_key = _generate_cache_key(model_name, system_message, user_content, max_tokens, response_model)

    def _do_call():
        anthropic_client = Anthropic(api_key=api_key)
        formatted_content = format_content_for_anthropic(user_content)
        client = instructor.from_anthropic(
            anthropic_client, mode=instructor.Mode.ANTHROPIC_TOOLS
        )
        return client.chat.completions.create(
            model=model_name,
            system=system_message,
            messages=[{"role": "user", "content": formatted_content}],
            max_tokens=max_tokens,
            temperature=temperature,
            response_model=response_model,
        )

    return _invoke_with_cache(
        _do_call, cache_key, response_model,
        "cached_llm_invoke: using cached result"
    )
    # --- original body of cached_llm_invoke END ---

def _cached_openai_invoke(
    model_name: str = "gpt-4.1",
    system_message: str = "",
    user_content: list = [],
    max_tokens: int = 2048,
    temperature: float = 0,
    response_model=None,
):
    """OpenAI Chat implementation using instructor + caching."""
    if OpenAI is None:
        raise ImportError("openai package not available")
    # Enforce OpenAI-mini family quirks
    special_models = {"o4-mini", "o3", "o1", "o1-pro"}
    if model_name in special_models:
        temperature = 1                          # required by those models

    _log_request_details(model_name, system_message, user_content,
                         max_tokens, temperature, provider="openai")

    cache_key = _generate_cache_key(
        f"openai:{model_name}",
        system_message,
        {"content": user_content},
        max_tokens,
        response_model,
    )

    def _do_call():
        # Build the message list only when we actually hit the API
        if isinstance(user_content, list):
            import json as _json
            parts = []
            for item in user_content:
                if isinstance(item, dict) and "text" in item:
                    parts.append(str(item["text"]))
                else:
                    parts.append(_json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else str(item))
            content_str = "\n".join(parts)
        else:
            content_str = str(user_content)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user",   "content": content_str},
        ]

        client = instructor.from_openai(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
        token_kwarg = (
            {"max_completion_tokens": max_tokens}
            if model_name in {"o4-mini", "o3", "o1", "o1-pro"}
            else {"max_tokens": max_tokens}
        )
        return client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            response_model=response_model,
            **token_kwarg,
        )

    return _invoke_with_cache(
        _do_call, cache_key, response_model,
        "cached_llm_invoke (openai): using cached result"
    )

def cached_llm_invoke(
    model_name: str | None = None,
    system_message: str = "",
    user_content: list = [],
    max_tokens: int = 2048,
    temperature: float = 0,
    response_model=None,
    provider: str = "anthropic", 
):
    """
    Unified entry point.  Set provider to 'anthropic'/'claude' (default)
    or 'openai' to route the request.
    """
    if model_name is None:
        # Allow override via environment variable set by CLI
        model_name = os.environ.get("LLM_MODEL_NAME")
    provider = provider.lower()
    logger.info("Dispatching call to %s provider (model=%s)", provider, model_name or "<default>")
    if provider in {"anthropic", "claude"}:
        return _cached_claude_invoke(
            model_name,
            system_message,
            user_content,
            max_tokens,
            temperature,
            response_model,
        )
    elif provider == "openai":
        return _cached_openai_invoke(
            model_name or "gpt-4.1",   # sensible default for OpenAI
            system_message,
            user_content,
            max_tokens,
            temperature,
            response_model,
        )
    else:
        raise ValueError(f"Unknown provider '{provider}'")

__all__ = [
    "get_claude_model_name",
    "cached_llm_invoke",
    "_openai_upload_file",
    "_cached_claude_invoke",
    "_cached_openai_invoke",
    "_invoke_with_cache",
]

def _openai_upload_file(client: "OpenAI", file_path: str):
    """
    Upload *file_path* to the OpenAI ‟files” endpoint and return the new file id.
    Caches by SHA-256 so we do not re-upload identical content in the same run.
    """
    import hashlib, pathlib

    abs_path = pathlib.Path(file_path).expanduser().resolve()
    digest   = hashlib.sha256(abs_path.read_bytes()).hexdigest()

    # keep an in-memory map {digest: file_id} to avoid multiple network calls
    if not hasattr(_openai_upload_file, "_memo"):
        _openai_upload_file._memo = {}
    if digest in _openai_upload_file._memo:
        return _openai_upload_file._memo[digest]

    resp = client.files.create(
        file=open(abs_path, "rb"),
        purpose="user_data",
    )
    file_id = resp.id
    _openai_upload_file._memo[digest] = file_id
    logger.info("Uploaded %s to OpenAI (file_id=%s)", abs_path.name, file_id)
    return file_id
