import base64
import diskcache
from enum import Enum, EnumMeta
import hashlib
import json
import os
from pathlib import Path
from textwrap import indent
from typing import Any, Callable, get_origin, get_args, List, Dict, Union

from anthropic import Anthropic
from openai import OpenAI
from pydantic import BaseModel, Field, create_model
from pydantic.fields import PydanticUndefined 

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
                file_data = base64.standard_b64encode(open(item, 'rb')).decode("utf-8")
                formatted_content.append({"type": "document",
                                          "source": { "type": "base64",
                                                      "media_type": "application/pdf",
                                                      "data": file_data }})
            else:
                raise ValueError("Item is not a Path, dict, or str")
        return formatted_content
    else:
        return [{"type": "text", "text": content}]

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

def _cached_claude_invoke(
    model_name: str | None = None,
    system_message: str = "",
    user_content: list = [],
    max_tokens: int = 2048,
    temperature: float = 0,
    response_model=None,
):
    """Anthropic/Claude implementation (code formerly in cached_llm_invoke)."""
    # Get the Anthropic API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    _log_request_details(model_name, system_message, user_content,
                         max_tokens, temperature, provider="anthropic")

    cache_key = _generate_cache_key("anthropic", model_name, system_message, user_content, max_tokens, response_model)

    def _do_call():
        anthropic_client = Anthropic(api_key=api_key)
        formatted_content = format_content_for_anthropic(user_content)
        return anthropic_client.chat.completions.create(
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

def _simplify_pydantic_model(model_cls: type[BaseModel]) -> type[BaseModel]:
    """
    Return a new Pydantic model where every field’s annotation is reduced to one of:
        str | int | float | bool | dict | list | Enum | Union[...]  (anyOf)

    – Scalars / containers already in that set are kept as-is.
    – Enum subclasses are preserved.
    – typing.List / typing.Dict collapse to bare list / dict.
    – Union / Optional is rebuilt from simplified members (deduplicated when possible).
    – Nested Pydantic models downgrade to dict.
    – Everything else falls back to str.

    OpenAI's structured responses needs the model to be simplified in this manner.
    """
    BASIC_SCALARS = {str, int, float, bool}
    BASIC_CONTAINERS = {dict, list}
    BASIC_ALLOWED = BASIC_SCALARS | BASIC_CONTAINERS

    def _simplify_type(tp: Any) -> Any:
        """
        Map *tp* to one of the allowed basic types
        (str | int | float | bool | dict | list | Enum | Union[..]).
        For containers, also simplify their parameter types so the JSON-schema
        still has `items` / `additionalProperties` metadata.
        """
        origin = get_origin(tp)

        # ── 1. keep scalars & Enum ──────────────────────────────────────────
        if tp in {str, int, float, bool} or isinstance(tp, EnumMeta):
            return tp

        # ── 2. typing.List / list[...] ──────────────────────────────────────
        if origin in (list, List):
            args = get_args(tp)
            elem = _simplify_type(args[0]) if args else str          # default str
            return List[elem]                                         # → list[elem]

        # ── 3. typing.Dict / dict[...] ──────────────────────────────────────
        if origin in (dict, Dict):
            args = get_args(tp)
            key   = _simplify_type(args[0]) if args else str
            value = _simplify_type(args[1]) if len(args) == 2 else str
            return Dict[key, value]                                   # → dict[key, value]

        # ── 4. Union / Optional (JSON-schema anyOf) ────────────────────────
        if origin is Union:
            simplified = tuple(_simplify_type(a) for a in get_args(tp))
            return Union[simplified]                                  # anyOf

        # ── 5. nested Pydantic model → dict ────────────────────────────────
        if isinstance(tp, type) and issubclass(tp, BaseModel):
            return Dict[str, Any]                                     # keep JSON object

        # ── 6. fallback ────────────────────────────────────────────────────
        return str

    def _clone_field_v2(name: str, model_field) -> tuple[type[Any], Field]:
        """
        Build a (type, FieldInfo) tuple suitable for `create_model` in Pydantic v2.
        """
        # ── 1. decide the default / default_factory ─────────────────────────
        if model_field.default_factory is not None:
            default_kw = {"default_factory": model_field.default_factory}
        elif model_field.default is not PydanticUndefined:
            default_kw = {"default": model_field.default}
        else:
            default_kw = {"default": ...}          # required field

        # ── 2. common metadata we want to carry over ────────────────────────
        meta_kw = {
            "alias": model_field.alias,            # None ⇢ no alias set
            "title": model_field.title,
            "description": model_field.description,
            "json_schema_extra": model_field.json_schema_extra,
            # numeric / length constraints that still exist in v2
            "gt": getattr(model_field, "gt", None),
            "ge": getattr(model_field, "ge", None),
            "lt": getattr(model_field, "lt", None),
            "le": getattr(model_field, "le", None),
            "min_length": getattr(model_field, "min_length", None),
            "max_length": getattr(model_field, "max_length", None),
            "pattern": getattr(model_field, "pattern", None),
            "frozen": getattr(model_field, "frozen", None),  # replaces allow_mutation
        }
        # strip Nones so we don’t pass unnecessary kwargs
        meta_kw = {k: v for k, v in meta_kw.items() if v is not None}

        # ── 3. build the new FieldInfo object ───────────────────────────────
        field_info = Field(**default_kw, **meta_kw)

        return model_field.annotation, field_info

    new_fields: dict[str, tuple[Any, Field]] = {}
    for name, mdl_field in model_cls.model_fields.items(): 
        simplified_type = _simplify_type(mdl_field.annotation)
        _, field_info = _clone_field_v2(name, mdl_field)
        new_fields[name] = (simplified_type, field_info)
    return create_model(f"{model_cls.__name__}Simplified", **new_fields) 

def _complexify_model(
    original_cls: type[BaseModel],
    simplified_instance: BaseModel,
) -> BaseModel:
    """
    Convert *simplified_instance* (produced by `simplify_pydantic_model`)
    back into an instance of *original_cls*.

    Pydantic’s own parsing logic handles the up-casting:
    ─ str → datetime / Path / bytes / …  
    ─ dict → nested BaseModel  
    ─ str / int → Enum, etc.
    """

    logger.info(f"_complexify_model: {simplified_instance.model_dump_json(indent=2)}")
    return original_cls.parse_obj(
        simplified_instance.dict(by_alias=True)  # keep aliases if any
    )


def _cached_openai_invoke(
    model_name: str = "gpt-4.1",
    system_message: str = "",
    user_content: list = [],
    max_tokens: int = 2048,
    temperature: float = 0,
    response_model=None,
):
    """OpenAI Chat implementation using caching."""
    special_models = {"o4-mini", "o3", "o1", "o1-pro"}
    if model_name in special_models:
        temperature = 1 

    _log_request_details(model_name, system_message, user_content,
                         max_tokens, temperature, provider="openai")


    cache_key = _generate_cache_key(
        "openai",
        model_name,
        system_message,
        user_content,
        max_tokens,
        response_model
    )

    def _do_call():
        raw_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        simplified_response_model = _simplify_pydantic_model(response_model)

        content_parts = []
        if isinstance(user_content, list):
            for item in user_content:
                if isinstance(item, Path):
                    file_id   = _openai_upload_file(raw_client, item)
                    content_parts.append({"type": "input_file", "file_id": file_id})
                elif isinstance(item, dict) and "text" in item:
                    content_parts.append({"type": "input_text",
                                          "text": str(item["text"])})
                else:
                    content_parts.append({"type": "input_text", "text": str(item)})
        else:
            content_parts.append({"type": "input_text", "text": str(user_content)})

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user",   "content": content_parts},
        ]

        import pprint
        logger.info(pprint.pprint(response_model.schema()))
        logger.info(pprint.pprint(simplified_response_model.schema()))

        response = raw_client.responses.parse(
            model=model_name,
            input=messages,
            text_format=simplified_response_model
        )

        complex_model = _complexify_model(response_model, response.output_parsed)

        return response.output_parsed

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
    "cached_llm_invoke",
    "_openai_upload_file",
    "_cached_claude_invoke",
    "_cached_openai_invoke",
    "_invoke_with_cache",
]

def _openai_upload_file(client: "OpenAI", file_path: Path):
    """
    Upload *file_path* to the OpenAI ‟files” endpoint and return the new file id.
    Caches by SHA-256 so we do not re-upload identical content in the same run.
    """

    abs_path = file_path.expanduser().resolve()
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
