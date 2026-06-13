from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path


HEX_COLOR = re.compile(
    r"^#[0-9a-fA-F]{6}$"
)

EXPECTED_COORDINATES = {
    f"{bank}{index}"
    for bank in "abcd"
    for index in range(8)
}


def validate(
    rendered_theme: Path,
    output_root: Path,
) -> None:
    del output_root

    if shutil.which("starship") is None:
        raise RuntimeError(
            "starship is not installed or is not available in PATH"
        )

    text = rendered_theme.read_text(
        encoding="utf-8"
    )

    if "{{" in text or "}}" in text:
        raise RuntimeError(
            "generated Starship palette contains unresolved placeholders"
        )

    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise RuntimeError(
            f"invalid Starship palette TOML: {error}"
        ) from error

    palettes = data.get("palettes")

    if not isinstance(palettes, dict):
        raise RuntimeError(
            "generated Starship output is missing [palettes]"
        )

    palette = palettes.get("b2t")

    if not isinstance(palette, dict):
        raise RuntimeError(
            "generated Starship output is missing [palettes.b2t]"
        )

    coordinates = set(palette)

    missing = sorted(
        EXPECTED_COORDINATES - coordinates
    )

    unexpected = sorted(
        coordinates - EXPECTED_COORDINATES
    )

    if missing:
        raise RuntimeError(
            "Starship palette is missing coordinates: "
            + ", ".join(missing)
        )

    if unexpected:
        raise RuntimeError(
            "Starship palette contains unexpected coordinates: "
            + ", ".join(unexpected)
        )

    for coordinate in sorted(EXPECTED_COORDINATES):
        value = palette[coordinate]

        if not isinstance(value, str):
            raise RuntimeError(
                f"{coordinate} must be a string"
            )

        if not HEX_COLOR.fullmatch(value):
            raise RuntimeError(
                f"{coordinate} has invalid color: {value!r}"
            )

    minimal_config = f'''palette = "b2t"
format = "$character"

[character]
success_symbol = "[>](a0)"
error_symbol = "[>](d6)"

{text}
'''

    try:
        tomllib.loads(minimal_config)
    except tomllib.TOMLDecodeError as error:
        raise RuntimeError(
            f"combined Starship test configuration is invalid: {error}"
        ) from error

    with tempfile.TemporaryDirectory(
        prefix="base2tone-tools-starship-"
    ) as temporary_directory:
        config_path = (
            Path(temporary_directory)
            / "starship.toml"
        )

        config_path.write_text(
            minimal_config,
            encoding="utf-8",
        )

        environment = os.environ.copy()
        environment.setdefault("TERM", "xterm-256color")
        environment["STARSHIP_CONFIG"] = str(config_path)
        environment["STARSHIP_SHELL"] = "zsh"

        process = subprocess.run(
            [
                "starship",
                "prompt",
                "--status",
                "0",
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
                or f"starship returned {process.returncode}"
            )

        if process.stderr.strip():
            raise RuntimeError(
                "starship reported an error: "
                + process.stderr.strip()
            )
