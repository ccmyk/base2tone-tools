from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


RGB_LINE = re.compile(r'\b(fg|bg|black|red|green|yellow|blue|magenta|cyan|white|orange)\s+\d+\s+\d+\s+\d+\b')


def validate(rendered_theme: Path, output_root: Path) -> None:
    del output_root

    text = rendered_theme.read_text(encoding="utf-8")

    if "{{" in text or "}}" in text:
        raise RuntimeError("generated Zellij theme contains unresolved placeholders")

    if 'base2tone' not in text:
        raise RuntimeError("generated Zellij theme is missing base2tone theme")

    if len(RGB_LINE.findall(text)) < 10:
        raise RuntimeError("generated Zellij theme contains too few RGB fields")

    if shutil.which("zellij") is None:
        return

    with tempfile.TemporaryDirectory(prefix="base2tone-tools-zellij-") as td:
        root = Path(td)
        config = root / "config.kdl"
        config.write_text(
            text + '\ntheme "base2tone"\nsimplified_ui true\npane_frames false\n',
            encoding="utf-8",
        )

        process = subprocess.run(
            [
                "zellij",
                "--config-dir",
                str(root),
                "setup",
                "--check",
            ],
            capture_output=True,
            text=True,
        )

    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or "zellij validation failed")
