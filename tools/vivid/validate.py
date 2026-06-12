from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def validate(
    rendered_theme: Path,
    output_root: Path,
) -> None:
    if shutil.which("zsh") is None:
        raise RuntimeError(
            "zsh is not installed or is not available in PATH"
        )

    ls_colors_fragment = (
        rendered_theme.parent / "ls-colors.zsh"
    )

    if not ls_colors_fragment.is_file():
        raise RuntimeError(
            f"Missing generated fragment: {ls_colors_fragment}"
        )

    try:
        subprocess.run(
            [
                "zsh",
                "-f",
                "-c",
                'source "$1"; [[ -n "$LS_COLORS" ]]',
                "_",
                str(ls_colors_fragment),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        message = error.stderr.strip()

        raise RuntimeError(
            message
            or "generated LS_COLORS fragment did not load"
        ) from error
