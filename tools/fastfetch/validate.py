from __future__ import annotations

import re
import shutil
import subprocess
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
            "generated Fastfetch configuration contains unresolved placeholders"
        )

    colors = set(HEX_COLOR.findall(text))

    if len(colors) < EXPECTED_COORDINATE_COLORS:
        raise RuntimeError(
            "generated Fastfetch configuration does not contain "
            "the expected Base2Tone color mappings"
        )

    fastfetch = shutil.which("fastfetch")

    if fastfetch is None:
        raise RuntimeError(
            "fastfetch is not installed or is not available in PATH"
        )

    # Override the configured module list so validation does not repeatedly
    # execute cache, Docker, storage, and mount inspection commands.
    process = subprocess.run(
        [
            fastfetch,
            "--config",
            str(rendered_theme),
            "--structure",
            "title",
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
