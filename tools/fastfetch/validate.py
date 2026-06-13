from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}")

EXPECTED_COORDINATE_COLORS = 7


def validate(
    rendered_theme: Path,
    output_root: Path,
) -> None:
    del output_root

    text = rendered_theme.read_text(encoding="utf-8")

    if "{{" in text or "}}" in text:
        raise RuntimeError(
            "generated Fastfetch theme fragment contains unresolved placeholders"
        )

    try:
        theme = json.loads(text)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"generated Fastfetch theme fragment is invalid JSON: {error}"
        ) from error

    display = theme.get("display")

    if not isinstance(display, dict):
        raise RuntimeError(
            "generated Fastfetch theme fragment is missing display"
        )

    colors = set(HEX_COLOR.findall(text))

    if len(colors) < EXPECTED_COORDINATE_COLORS:
        raise RuntimeError(
            "generated Fastfetch theme fragment does not contain "
            "the expected Base2Tone color mappings"
        )

    fastfetch = shutil.which("fastfetch")

    if fastfetch is None:
        raise RuntimeError(
            "fastfetch is not installed or is not available in PATH"
        )

    # Merge the color fragment into a minimal config so validation does not
    # require the personal Fastfetch module list or system commands.
    config = {
        "$schema": (
            "https://github.com/fastfetch-cli/fastfetch/raw/dev/"
            "doc/json_schema.json"
        ),
        "logo": {
            "type": "none",
        },
        "display": {
            "separator": "  ",
            "brightColor": False,
            **display,
        },
        "modules": [
            "title",
        ],
    }

    with tempfile.TemporaryDirectory(
        prefix="base2tone-tools-fastfetch-"
    ) as temporary_directory:
        config_path = Path(temporary_directory) / "config.jsonc"
        config_path.write_text(
            json.dumps(config, indent=2) + "\n",
            encoding="utf-8",
        )

        process = subprocess.run(
            [
                fastfetch,
                "--config",
                str(config_path),
                "--pipe",
            ],
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
            or f"fastfetch validation returned {process.returncode}"
        )