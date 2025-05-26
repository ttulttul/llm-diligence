#!/usr/bin/env python3
"""
json2doc.py – validate a JSON file with a selected Pydantic model and output
either Markdown (default) or HTML.

Examples
--------
# List available models
./json2doc.py --list

# Render Markdown with selected model
./json2doc.py --model nda_NonDisclosureAgreement sample.json

# Render HTML instead
./json2doc.py --model nda_NonDisclosureAgreement --html sample.json
"""

import argparse
import json
import html
from pathlib import Path
from typing import Any, Dict

from models.base import get_available_models

# --------------------------------------------------------------------------- #
# helpers                                                                     #
# --------------------------------------------------------------------------- #
def _md(val: Any, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(val, dict):
        lines = []
        for k, v in val.items():
            pretty = k.replace("_", " ").title()
            lines.append(f"{pad}- **{pretty}:**")
            lines.append(_md(v, indent + 2))
        return "\n".join(lines)
    if isinstance(val, list):
        return "\n".join(f"{pad}- {item}" for item in val)
    return f"{pad}{val}"


def _html(val: Any) -> str:
    if isinstance(val, dict):
        items = [
            f"<li><strong>{html.escape(k.replace('_', ' ').title())}:</strong>{_html(v)}</li>"
            for k, v in val.items()
        ]
        return "<ul>" + "".join(items) + "</ul>"
    if isinstance(val, list):
        return "<ul>" + "".join(f"<li>{_html(item)}</li>" for item in val) + "</ul>"
    return f" {html.escape(str(val))}"


def render_markdown(model_instance) -> str:
    body = _md(model_instance.model_dump())
    title = getattr(model_instance, "agreement_title", model_instance.__class__.__name__)
    return f"# {title}\n\n{body}"


def render_html(model_instance) -> str:
    body = _html(model_instance.model_dump())
    title = html.escape(
        getattr(model_instance, "agreement_title", model_instance.__class__.__name__)
    )
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title></head><body><h1>{title}</h1>{body}</body></html>"


# --------------------------------------------------------------------------- #
# CLI                                                                         #
# --------------------------------------------------------------------------- #
def main() -> None:
    models_dict: Dict[str, type] = get_available_models()

    ap = argparse.ArgumentParser(
        description="Validate JSON with a selected model and output Markdown or HTML."
    )
    ap.add_argument("--list", action="store_true", help="List available model keys and exit")
    ap.add_argument("--model", help="Key of the model to use (see --list)")
    ap.add_argument(
        "--html", action="store_true", help="Output HTML instead of Markdown"
    )
    ap.add_argument("json", nargs="?", help="Path to the JSON file to load")
    args = ap.parse_args()

    if args.list:
        print("\n".join(sorted(models_dict)))
        return

    if not args.json:
        ap.error("JSON file path required (or use --list).")

    # pick model
    if args.model:
        try:
            Model = models_dict[args.model]
        except KeyError:
            ap.error(f"Unknown model '{args.model}'. Use --list to see options.")
    else:
        if len(models_dict) != 1:
            ap.error("Multiple models available; you must specify --model.")
        Model = next(iter(models_dict.values()))

    # load & validate
    data = json.loads(Path(args.json).read_text())
    instance = Model(**data)  # Pydantic validation

    # output
    if args.html:
        print(render_html(instance))
    else:
        print(render_markdown(instance))


if __name__ == "__main__":
    main()
