#!/usr/bin/env python3
"""
json2md.py – CLI to render any Pydantic model instance stored in JSON as Markdown.

Usage examples:
  # Show all known models
  ./json2md.py --list

  # Validate sample.json with the NonDisclosureAgreement model
  ./json2md.py --model nda_NonDisclosureAgreement sample.json
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from models.base import get_available_models

def _to_md(val: Any, indent: int = 0) -> str:
    """Recursively render a Python object as indented Markdown."""
    pad = " " * indent
    if isinstance(val, dict):
        lines = []
        for k, v in val.items():
            pretty = k.replace("_", " ").title()
            lines.append(f"{pad}- **{pretty}:**")
            lines.append(_to_md(v, indent + 2))
        return "\n".join(lines)
    if isinstance(val, list):
        return "\n".join(f"{pad}- {item}" for item in val)
    return f"{pad}{val}"


def render_markdown(model_instance) -> str:
    body = _to_md(model_instance.model_dump())
    title = getattr(model_instance, "agreement_title", model_instance.__class__.__name__)
    return f"# {title}\n\n{body}"

def main() -> None:
    models_dict: Dict[str, type] = get_available_models()

    ap = argparse.ArgumentParser(description="Validate JSON with a selected model and output Markdown.")
    ap.add_argument("--list", action="store_true", help="List available model keys and exit")
    ap.add_argument("--model", help="Key of the model to use (see --list)")
    ap.add_argument("json", nargs="?", help="Path to the JSON file to load")

    args = ap.parse_args()

    # --list: just dump the available keys and quit
    if args.list:
        for key in sorted(models_dict):
            print(key)
        return

    if not args.json:
        ap.error("JSON file path required (or use --list).")

    # pick the model
    if args.model:
        try:
            Model = models_dict[args.model]
        except KeyError:
            ap.error(f"Unknown model '{args.model}'. Use --list to see options.")
    else:
        # no --model supplied: choose the sole model if exactly one exists
        if len(models_dict) != 1:
            ap.error("Multiple models available; you must specify --model.")
        Model = next(iter(models_dict.values()))

    # load & validate
    data = json.loads(Path(args.json).read_text())
    instance = Model(**data)  # Pydantic validation
    print(render_markdown(instance))


if __name__ == "__main__":
    main()
