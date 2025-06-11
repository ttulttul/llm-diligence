import hashlib, json, os
from pathlib import Path
from typing import Any, Callable, get_origin, get_args, List, Dict, Union
from enum import EnumMeta
from openai import OpenAI
from pydantic import BaseModel, Field, create_model, ConfigDict
from pydantic.fields import PydanticUndefined
from pydantic_core import ValidationError as CoreValidationError

from utils import logger
from utils.llm import (
    _generate_cache_key,
    _invoke_with_cache,
    _log_request_details,
    _log_llm_response,
    warn_on_empty_or_missing_fields
)

# utils/llm_openai.py   (add after imports)
_SIMPLIFIED_MODEL_CACHE: dict[type[BaseModel], type[BaseModel]] = {}

def _simplify_pydantic_model(model_cls: type[BaseModel]) -> type[BaseModel]:
    # ── cache check ─────────────────────────────────────────────
    if model_cls in _SIMPLIFIED_MODEL_CACHE:
        return _SIMPLIFIED_MODEL_CACHE[model_cls]
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

        # ── 5. nested Pydantic model → simplified model ────────────────────
        # new – recursively simplify nested models so each gets
        # `additionalProperties: false` in its own schema.
        if isinstance(tp, type) and issubclass(tp, BaseModel):
            return _simplify_pydantic_model(tp)

        # ── 6. fallback ────────────────────────────────────────────────────
        return str

    def _clone_field_v2(name: str, model_field) -> tuple[type[Any], Field]:
        """
        Build a (type, FieldInfo) tuple suitable for `create_model` in Pydantic v2,
        but without propagating defaults – OpenAI rejects `default` in the schema.
        """
        # ── only carry metadata we still want ─────────────────────────────
        meta_kw = {
            "alias":          model_field.alias,
            "title":          model_field.title,
            "description":    model_field.description,
            "json_schema_extra": model_field.json_schema_extra,
            "gt": getattr(model_field, "gt", None),
            "ge": getattr(model_field, "ge", None),
            "lt": getattr(model_field, "lt", None),
            "le": getattr(model_field, "le", None),
            "min_length": getattr(model_field, "min_length", None),
            "max_length": getattr(model_field, "max_length", None),
            "pattern": getattr(model_field, "pattern", None),
            "frozen": getattr(model_field, "frozen", None),
        }
        meta_kw = {k: v for k, v in meta_kw.items() if v is not None}

        # no default / default_factory passed ➜ no "default" in schema
        field_info = Field(**meta_kw)

        return model_field.annotation, field_info

    new_fields: dict[str, tuple[Any, Field]] = {}
    for name, mdl_field in model_cls.model_fields.items(): 
        simplified_type = _simplify_type(mdl_field.annotation)
        _, field_info = _clone_field_v2(name, mdl_field)
        new_fields[name] = (simplified_type, field_info)
    # OpenAI requires `additionalProperties` to be present and set to false.
    cfg = ConfigDict(extra="forbid")          # ⇒ additionalProperties: false

    simplified_cls = create_model(
        f"{model_cls.__name__}Simplified",
        __config__=cfg,                       # attach the “extra-forbid” config
        **new_fields
    )
    _SIMPLIFIED_MODEL_CACHE[model_cls] = simplified_cls
    return simplified_cls

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

    logger.debug(f"_complexify_model: {simplified_instance.model_dump_json(indent=2)}")

    try:
        raw_data = simplified_instance.dict(by_alias=True)   # keep aliases
        return original_cls.model_validate(raw_data)         # ← use v2 validator
    except CoreValidationError as exc:
        # Emit a detailed error message then re-raise so callers can decide what to do.
        logger.error(
            "Validation error while reconstructing %s from simplified LLM response",
            original_cls.__name__
        )
        raise

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

def cached_llm_invoke(
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

        logger.info(f"Sending request to OpenAI... {messages}")

        response = raw_client.responses.parse(
            model=model_name,
            input=messages,
            text_format=simplified_response_model
        )
        logger.debug("Raw OpenAI response: %s", response)

        warn_on_empty_or_missing_fields(response.output_parsed.model_dump(),
                                        response_model)

        complex_model = _complexify_model(response_model, response.output_parsed)

        return response.output_parsed

    return _invoke_with_cache(
        _do_call, cache_key, response_model,
        "cached_llm_invoke (openai): using cached result"
    )
