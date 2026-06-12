from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path


EXPECTED_SECTIONS = {
    "flavor",
    "app",
    "mgr",
    "tabs",
    "mode",
    "indicator",
    "status",
    "which",
    "confirm",
    "spot",
    "notify",
    "pick",
    "input",
    "cmp",
    "tasks",
    "help",
    "filetype",
    "icon",
}

EXPECTED_MGR_KEYS = {
    "cwd",
    "find_keyword",
    "find_position",
    "symlink_target",
    "marker_copied",
    "marker_cut",
    "marker_marked",
    "marker_selected",
    "marker_symbol",
    "count_copied",
    "count_cut",
    "count_selected",
    "border_symbol",
    "border_style",
    "syntect_theme",
}

EXPECTED_ICON_GROUPS = {
    "globs",
    "dirs",
    "files",
    "exts",
    "conds",
}

HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


def is_emoji(character: str) -> bool:
    value = ord(character)

    return (
        0x1F000 <= value <= 0x1FAFF
        or 0x1FC00 <= value <= 0x1FFFF
    )


def is_private_use(character: str) -> bool:
    value = ord(character)

    return (
        0xE000 <= value <= 0xF8FF
        or 0xF0000 <= value <= 0xFFFFD
        or 0x100000 <= value <= 0x10FFFD
    )


def validate_color(value: object, location: str) -> None:
    if not isinstance(value, str):
        raise RuntimeError(
            f"{location} color must be a string"
        )

    if value == "reset":
        return

    if not HEX_COLOR.fullmatch(value):
        raise RuntimeError(
            f"{location} has invalid color: {value!r}"
        )


def inspect_styles(value: object, location: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"

            if key in {"fg", "bg"}:
                validate_color(child, child_location)
            else:
                inspect_styles(child, child_location)

    elif isinstance(value, list):
        for index, child in enumerate(value):
            inspect_styles(
                child,
                f"{location}[{index}]",
            )


def validate_icon_rule(
    rule: object,
    group: str,
    index: int,
) -> None:
    location = f"[icon].{group}[{index}]"

    if not isinstance(rule, dict):
        raise RuntimeError(
            f"{location} must be a table"
        )

    selector = "if" if group == "conds" else (
        "url" if group == "globs" else "name"
    )

    if selector not in rule:
        raise RuntimeError(
            f"{location} is missing {selector!r}"
        )

    if "text" not in rule:
        raise RuntimeError(
            f"{location} is missing 'text'"
        )

    if not isinstance(rule["text"], str) or not rule["text"]:
        raise RuntimeError(
            f"{location}.text must be a non-empty string"
        )

    selector_value = rule[selector]

    if not isinstance(selector_value, str):
        raise RuntimeError(
            f"{location}.{selector} must be a string"
        )

    if any(is_emoji(character) for character in selector_value):
        raise RuntimeError(
            f"{location}.{selector} contains an emoji selector"
        )

    glyph = rule["text"]

    if any(is_emoji(character) for character in glyph):
        raise RuntimeError(
            f"{location}.text contains an emoji glyph"
        )

    if not any(is_private_use(character) for character in glyph):
        raise RuntimeError(
            f"{location}.text is not a Nerd Font private-use glyph"
        )

    if "fg" in rule:
        validate_color(rule["fg"], f"{location}.fg")


def validate(
    rendered_theme: Path,
    output_root: Path,
) -> None:
    del output_root

    try:
        with rendered_theme.open("rb") as file:
            data = tomllib.load(file)
    except tomllib.TOMLDecodeError as error:
        raise RuntimeError(
            f"invalid TOML syntax: {error}"
        ) from error

    actual_sections = set(data)
    missing_sections = sorted(
        EXPECTED_SECTIONS - actual_sections
    )

    if missing_sections:
        raise RuntimeError(
            "missing Yazi theme sections: "
            + ", ".join(missing_sections)
        )

    mgr = data.get("mgr")

    if not isinstance(mgr, dict):
        raise RuntimeError("[mgr] must be a table")

    missing_mgr_keys = sorted(
        EXPECTED_MGR_KEYS - set(mgr)
    )

    if missing_mgr_keys:
        raise RuntimeError(
            "[mgr] is incomplete: "
            + ", ".join(missing_mgr_keys)
        )

    filetype = data.get("filetype")

    if (
        not isinstance(filetype, dict)
        or not isinstance(filetype.get("rules"), list)
        or len(filetype["rules"]) < 10
    ):
        raise RuntimeError(
            "[filetype].rules is missing or incomplete"
        )

    icon = data.get("icon")

    if not isinstance(icon, dict):
        raise RuntimeError("[icon] must be a table")

    missing_icon_groups = sorted(
        EXPECTED_ICON_GROUPS - set(icon)
    )

    if missing_icon_groups:
        raise RuntimeError(
            "[icon] is missing groups: "
            + ", ".join(missing_icon_groups)
        )

    minimum_counts = {
        "globs": 0,
        "dirs": 10,
        "files": 200,
        "exts": 450,
        "conds": 10,
    }

    for group, minimum in minimum_counts.items():
        rules = icon[group]

        if not isinstance(rules, list):
            raise RuntimeError(
                f"[icon].{group} must be an array"
            )

        if len(rules) < minimum:
            raise RuntimeError(
                f"[icon].{group} is incomplete: "
                f"expected at least {minimum}, found {len(rules)}"
            )

        for index, rule in enumerate(rules):
            validate_icon_rule(rule, group, index)

    inspect_styles(data, "theme")

    if shutil.which("yazi") is None:
        raise RuntimeError(
            "Yazi is not installed or is not available in PATH"
        )

    with tempfile.TemporaryDirectory(
        prefix="base2tone-tools-yazi-"
    ) as temporary_directory:
        config_home = Path(temporary_directory)

        shutil.copy2(
            rendered_theme,
            config_home / "theme.toml",
        )

        environment = os.environ.copy()
        environment["YAZI_CONFIG_HOME"] = str(config_home)

        process = subprocess.run(
            ["yazi", "--debug"],
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
                or f"yazi --debug returned {process.returncode}"
            )
