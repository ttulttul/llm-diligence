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
    logger.debug(f"_generate_cache_key({combined}) -> {cache_key}")
    return cache_key

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

def _format_openai_messages(messages):
    """
    Ensure every message dict matches the OpenAI ‟responses.create” schema:
    each dict must contain `role` and its `content` must be a *list* of
    typed-content items, e.g.  {"type": "input_text", "text": "..."}.
    Strings are automatically wrapped.
    """
    formatted = []
    for m in messages:
        if not (isinstance(m, dict) and "role" in m):
            raise ValueError("Each message must be a dict with a 'role' key")
        # already in the correct format?
        if isinstance(m.get("content"), list):
            formatted.append(m)
        else:   # wrap plain-text content
            formatted.append(
                {
                    "role": m["role"],
                    "content": [
                        {
                            "type": "input_text",
                            "text": str(m["content"])
                        }
                    ]
                }
            )
    return formatted

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

    pretty = _pretty_format_user_content(user_content)
    logger.info("LLM query (model=%s, max_tokens=%d):\n%s", model_name, max_tokens, pretty)

    # Generate a cache key for this specific request
    cache_key = _generate_cache_key(model_name, system_message, user_content, max_tokens, response_model)
    
    # Check if the result is already cached
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        logger.info("cached_llm_invoke: using cached result")
        # If no response_model is provided, just return the cached string
        if response_model is None:
            _log_llm_response(cached_result)
            return cached_result
        # Otherwise deserialize the cached result
        _log_llm_response(cached_result)
        return response_model.model_validate_json(cached_result)
    
    # Initialize Anthropic client
    anthropic_client = Anthropic(api_key=api_key)
    
    # Format the content properly for the API
    formatted_content = format_content_for_anthropic(user_content)
    
    # Set up instructor client
    client = instructor.from_anthropic(
        anthropic_client,
        mode=instructor.Mode.ANTHROPIC_TOOLS
    )
    
    # Make the API call with instructor
    result = client.chat.completions.create(
        model=model_name,
        system=system_message,
        messages=[
            {"role": "user", "content": formatted_content}
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        response_model=response_model
    )

    _log_llm_response(result)

    # Cache the result
    if response_model is not None:
        serialized_result = result.model_dump_json()
        cache.set(cache_key, serialized_result)
        return result
    else:
        # For simple text responses
        text_result = result
        cache.set(cache_key, text_result)
        return text_result
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

    # Prepare logging text exactly like _pretty_format_user_content does
    pretty = _pretty_format_user_content(user_content)
    logger.info("LLM query (model=%s, max_tokens=%d):\n%s", model_name, max_tokens, pretty)

    cache_key = _generate_cache_key(
        f"openai:{model_name}",
        system_message,
        {"content": user_content},
        max_tokens,
        response_model,
    )
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        logger.info("cached_llm_invoke (openai): using cached result")
        if response_model is None:
            _log_llm_response(cached_result)
            return cached_result
        _log_llm_response(cached_result)
        return response_model.model_validate_json(cached_result)

    # Convert list / dict rich-content into plain string for OpenAI
    if isinstance(user_content, list):
        import json as _json
        parts: list[str] = []
        for item in user_content:
            if isinstance(item, dict):
                # prefer the "text" field if present (Anthropic-style item)
                if "text" in item:
                    parts.append(str(item["text"]))
                else:
                    parts.append(_json.dumps(item, ensure_ascii=False))
            else:
                parts.append(str(item))
        content_str = "\n".join(parts)
    else:
        content_str = str(user_content)
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": content_str},
    ]

    # Build instructor-wrapped OpenAI client
    client = instructor.from_openai(
        OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
    )

    # Build the token-argument dynamically
    token_kwarg = (
        {"max_completion_tokens": max_tokens}
        if model_name in special_models
        else {"max_tokens": max_tokens}
    )

    result = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        response_model=response_model,
        **token_kwarg,                # <-- use correct param name
    )

    _log_llm_response(result)
    # Cache + return
    if response_model is not None:
        cache.set(cache_key, result.model_dump_json())
        return result
    cache.set(cache_key, result)
    return result

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
    "_cached_claude_invoke",      # NEW
    "_cached_openai_invoke",      # NEW
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
