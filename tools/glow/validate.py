from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")

EXPECTED_SECTIONS = {
    "document",
    "block_quote",
    "paragraph",
    "list",
    "heading",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "text",
    "strikethrough",
    "emph",
    "strong",
    "hr",
    "item",
    "enumeration",
    "task",
    "link",
    "link_text",
    "image",
    "image_text",
    "code",
    "code_block",
    "table",
    "definition_list",
    "definition_term",
    "definition_description",
    "html_block",
    "html_span",
}

EXPECTED_CHROMA_FIELDS = {
    "text",
    "error",
    "comment",
    "comment_preproc",
    "keyword",
    "keyword_reserved",
    "keyword_namespace",
    "keyword_type",
    "operator",
    "punctuation",
    "name",
    "name_builtin",
    "name_tag",
    "name_attribute",
    "name_class",
    "name_constant",
    "name_decorator",
    "name_exception",
    "name_function",
    "name_other",
    "literal",
    "literal_number",
    "literal_date",
    "literal_string",
    "literal_string_escape",
    "generic_deleted",
    "generic_emph",
    "generic_inserted",
    "generic_strong",
    "generic_subheading",
    "background",
}


def inspect_colors(value: object, location: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"

            if key in {"color", "background_color"}:
                if not isinstance(child, str):
                    raise RuntimeError(
                        f"{child_location} must be a string"
                    )

                if not HEX_COLOR.fullmatch(child):
                    raise RuntimeError(
                        f"{child_location} has invalid color: {child!r}"
                    )
            else:
                inspect_colors(child, child_location)

    elif isinstance(value, list):
        for index, child in enumerate(value):
            inspect_colors(child, f"{location}[{index}]")


def validate(
    rendered_theme: Path,
    output_root: Path,
) -> None:
    del output_root

    try:
        data = json.loads(rendered_theme.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"invalid JSON syntax: {error}"
        ) from error

    if not isinstance(data, dict):
        raise RuntimeError(
            "generated Glow style must be a JSON object"
        )

    missing_sections = sorted(EXPECTED_SECTIONS - set(data))

    if missing_sections:
        raise RuntimeError(
            "generated Glow style is missing sections: "
            + ", ".join(missing_sections)
        )

    code_block = data.get("code_block")

    if not isinstance(code_block, dict):
        raise RuntimeError(
            "code_block must be an object"
        )

    chroma = code_block.get("chroma")

    if not isinstance(chroma, dict):
        raise RuntimeError(
            "code_block.chroma must be an object"
        )

    missing_chroma = sorted(EXPECTED_CHROMA_FIELDS - set(chroma))

    if missing_chroma:
        raise RuntimeError(
            "code_block.chroma is missing fields: "
            + ", ".join(missing_chroma)
        )

    inspect_colors(data, "style")

    text = rendered_theme.read_text(encoding="utf-8")

    if re.search(r"\{\{\s*[ABCD][0-7]\s*\}\}", text):
        raise RuntimeError(
            "generated Glow style contains unresolved coordinates"
        )

    if shutil.which("glow") is None:
        raise RuntimeError(
            "glow is not installed or is not available in PATH"
        )

    markdown = """# Glow validation

Normal text with **strong**, *emphasis*, and `inline code`.

> Block quote

- list item
- [x] completed task

~~~python
def greet(name: str) -> str:
    return f"Hello, {name}"
~~~

| field | value |
| --- | --- |
| scheme | Base2Tone |
"""

    with tempfile.TemporaryDirectory(
        prefix="base2tone-tools-glow-"
    ) as temporary_directory:
        temporary = Path(temporary_directory)
        markdown_path = temporary / "test.md"
        markdown_path.write_text(markdown, encoding="utf-8")

        environment = os.environ.copy()
        environment.setdefault("TERM", "xterm-256color")
        environment.pop("NO_COLOR", None)

        process = subprocess.run(
            [
                "glow",
                "--style",
                str(rendered_theme),
                "--width",
                "80",
                str(markdown_path),
            ],
            env=environment,
            capture_output=True,
            text=True,
        )

    if process.returncode != 0:
        message = (
            process.stderr.strip()
            or process.stdout.strip()
        )

        raise RuntimeError(
            message
            or f"glow validation exited with status {process.returncode}"
        )

    if not process.stdout.strip():
        raise RuntimeError(
            "glow produced no rendered output"
        )
