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
import sys
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
    source = getattr(model_instance, "source_filename", None)
    link_line = f"[Source PDF]({source})\n\n" if source else ""
    return f"# {title}\n\n{link_line}{body}"


def render_html(model_instance) -> str:
    body = _html(model_instance.model_dump())
    title = html.escape(
        getattr(model_instance, "agreement_title", model_instance.__class__.__name__)
    )
    source = getattr(model_instance, "source_filename", None)
    source_html = (
        f"<p><a href=\"{html.escape(str(source))}\">Source PDF</a></p>" if source else ""
    )
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/github-markdown-css@5.2.0/github-markdown.min.css\">"
        f"<title>{title}</title></head><body class=\"markdown-body\"><h1>{title}</h1>"
        f"{source_html}{body}</body></html>"
    )


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
    ap.add_argument("--index-columns", help="Comma-separated list of model field names to include as columns in the index table")
    ap.add_argument("json", nargs="?", help="Path to the JSON file to load")
    args = ap.parse_args()

    index_cols = [c.strip() for c in args.index_columns.split(",")] if getattr(args, "index_columns", None) else []

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

    json_path = Path(args.json)
    if json_path.is_dir():
        dir_path = json_path
        json_files = sorted(dir_path.glob("*.json"))
        rendered_docs: list[tuple[str, str, list[Any]]] = []
        error_count = 0
        for jf in json_files:
            try:
                data = json.loads(jf.read_text())
                instance = Model(**data)  # Pydantic validation
                out_ext = ".html" if args.html else ".md"
                out_file = jf.with_suffix(out_ext)
                content = render_html(instance) if args.html else render_markdown(instance)
                out_file.write_text(content, encoding="utf-8")
                title = getattr(instance, "agreement_title", instance.__class__.__name__)
                rendered_docs.append((title, out_file.name, [getattr(instance, col, None) for col in index_cols]))
            except Exception as exc:
                sys.stderr.write(f"Error processing {jf}: {exc}\n")
                error_count += 1

        # build index file
        if args.html:
            header_html = "<tr><th>Title</th>" + "".join(
                f"<th>{html.escape(col.replace('_', ' ').title())}</th>" for col in index_cols
            ) + "<th>File</th></tr>"
            rows = "".join(
                "<tr>"
                f"<td>{html.escape(title)}</td>"
                + "".join(f"<td>{_html(val)}</td>" for val in col_vals)
                + f"<td><a href=\"{fname}\">{html.escape(fname)}</a></td></tr>"
                for title, fname, col_vals in rendered_docs
            )
            index_content = (
                "<!doctype html><html><head><meta charset='utf-8'>"
                "<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/github-markdown-css@5.2.0/github-markdown.min.css\">"
                "<title>Documents Index</title></head><body class=\"markdown-body\">"
                "<h1>Documents</h1><table>"
                + header_html +
                rows +
                "</table></body></html>"
            )
            index_file = dir_path / "index.html"
        else:
            header_cells = ["Title", *[col.replace('_', ' ').title() for col in index_cols], "File"]
            header = "| " + " | ".join(header_cells) + " |\n" + "| " + " | ".join("---" for _ in header_cells) + " |\n"
            rows = "\n".join(
                "| "
                + " | ".join(
                    [title] + [_md(val).replace('\n', '<br>') for val in col_vals] + [f"[{fname}]({fname})"]
                )
                + " |"
                for title, fname, col_vals in rendered_docs
            )
            index_content = f"# Documents\n\n{header}{rows}\n"
            index_file = dir_path / "index.md"

        index_file.write_text(index_content, encoding="utf-8")
        print(f"Wrote {len(rendered_docs)} documents to {dir_path}. Index: {index_file} (errors: {error_count})")
        return
    else:
        # load & validate
        data = json.loads(json_path.read_text())
        instance = Model(**data)  # Pydantic validation

        # output
        if args.html:
            print(render_html(instance))
        else:
            print(render_markdown(instance))


if __name__ == "__main__":
    main()
