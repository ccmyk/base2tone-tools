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
        raise RuntimeError("generated Delta theme contains unresolved placeholders")

    if "[delta]" not in text:
        raise RuntimeError("generated Delta theme is missing [delta] section")

    if len(HEX.findall(text)) < 10:
        raise RuntimeError("generated Delta theme contains too few colors")

    if shutil.which("delta") is None:
        raise RuntimeError("delta is not installed or is not available in PATH")

    diff = """diff --git a/example.txt b/example.txt
index 1111111..2222222 100644
--- a/example.txt
+++ b/example.txt
@@ -1,3 +1,3 @@
 unchanged
-old value
+new value
 unchanged
"""

    with tempfile.TemporaryDirectory(prefix="base2tone-tools-delta-") as td:
        cfg = Path(td) / "theme.gitconfig"
        cfg.write_text(text, encoding="utf-8")

        process = subprocess.run(
            [
                "delta",
                "--config",
                str(cfg),
                "--no-gitconfig",
            ],
            input=diff,
            capture_output=True,
            text=True,
        )

    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or "delta validation failed")

    if not process.stdout.strip():
        raise RuntimeError("delta produced no output")
