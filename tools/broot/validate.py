from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


HEX = re.compile(r"#[0-9a-fA-F]{6}")


def validate(rendered_theme: Path, output_root: Path) -> None:
    del output_root

    text = rendered_theme.read_text(encoding="utf-8")

    if "{{" in text or "}}" in text:
        raise RuntimeError("generated Broot skin contains unresolved placeholders")

    if "skin:" not in text:
        raise RuntimeError("generated Broot skin is missing skin map")

    if len(HEX.findall(text)) < 20:
        raise RuntimeError("generated Broot skin contains too few colors")

    if shutil.which("broot") is None:
        return

    with tempfile.TemporaryDirectory(prefix="base2tone-tools-broot-") as td:
        root = Path(td)
        skin = root / "base2tone.hjson"
        conf = root / "conf.hjson"

        skin.write_text(text, encoding="utf-8")
        conf.write_text(
            'imports: [ "base2tone.hjson" ]\nmodal: false\n',
            encoding="utf-8",
        )

        process = subprocess.run(
            [
                "broot",
                "--conf",
                str(conf),
                "--version",
            ],
            capture_output=True,
            text=True,
        )

    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or "broot validation failed")
