from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def validate(
    rendered_theme: Path,
    output_root: Path,
) -> None:
    if shutil.which("eza") is None:
        raise RuntimeError(
            "eza is not installed or is not available in PATH"
        )

    with tempfile.TemporaryDirectory(
        prefix="base2tone-tools-eza-"
    ) as temporary_directory:
        config_directory = Path(temporary_directory)

        shutil.copy2(
            rendered_theme,
            config_directory / "theme.yml",
        )

        environment = os.environ.copy()
        environment.pop("LS_COLORS", None)
        environment.pop("EZA_COLORS", None)
        environment["EZA_CONFIG_DIR"] = str(config_directory)

        try:
            subprocess.run(
                [
                    "eza",
                    "--colour=always",
                    "--long",
                    "--git",
                    str(output_root),
                ],
                check=True,
                env=environment,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            message = error.stderr.strip()

            raise RuntimeError(
                message or f"eza exited with status {error.returncode}"
            ) from error
