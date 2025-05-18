import hashlib, json, os
from pathlib import Path
from typing import Any, Callable, get_origin, get_args, List, Dict, Union
from enum import EnumMeta
from openai import OpenAI
from pydantic import BaseModel, Field, create_model
from pydantic.fields import PydanticUndefined
from pydantic_core import ValidationError as CoreValidationError

from utils import logger
from utils.llm import (
    _generate_cache_key,
    _invoke_with_cache,
    _log_request_details,
    _log_llm_response,
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

    try:
        return original_cls.parse_obj(
            simplified_instance.dict(by_alias=True)   # keep aliases if any
        )
    except CoreValidationError as exc:
        # Emit a detailed error message then re-raise so callers can decide what to do.
        logger.error(
            "Validation error while reconstructing %s from simplified LLM response: %s\nRaw data: %s",
            original_cls.__name__, exc, simplified_instance.model_dump_json(indent=2)
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
