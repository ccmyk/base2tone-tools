from __future__ import annotations

import importlib.util
import re
import shutil
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path


ROOT          = Path(__file__).resolve().parent.parent
SCHEME_DIR    = ROOT / "vendor/Base2Tone/db/schemes"
TOOLS_DIR     = ROOT / "tools"
GENERATED_DIR = ROOT / "generated"
CURRENT_DIR   = GENERATED_DIR / "current"

EXPECTED_COORDINATES = tuple(
    f"{bank}{index}"
    for bank in "ABCD"
    for index in range(8)
)

PALETTE_PATTERN = re.compile(
    r"""(?mx)
    ^\s*
    base([ABCD])([0-7])
    \s*:\s*
    ['"]?
    ([0-9a-fA-F]{6})
    ['"]?
    \s*$
    """
)

PLACEHOLDER_PATTERN = re.compile(
    r"\{\{\s*([ABCD][0-7])\s*\}\}"
)

ANY_PLACEHOLDER_PATTERN = re.compile(
    r"\{\{\s*([^{}]+?)\s*\}\}"
)


class ThemeError(Exception):
    """Raised for expected scheme, module, or rendering errors."""


@dataclass(frozen=True)
class Palette:
    name: str
    source: Path
    colors: dict[str, str]


@dataclass(frozen=True)
class ToolModule:
    name: str
    directory: Path
    template: Path
    output: Path
    manifest: Path
    postprocess: Path | None


@dataclass(frozen=True)
class BuildResult:
    palette: Palette
    modules: tuple[ToolModule, ...]
    outputs: tuple[Path, ...]


def normalize_scheme(value: str) -> str:
    name = Path(value).name

    for suffix in (".yaml", ".yml"):
        if name.endswith(suffix):
            name = name.removesuffix(suffix)

    name = name.removeprefix("base2tone-")
    name = name.removesuffix("-dark")
    name = name.removesuffix("-light")

    if not name:
        raise ThemeError("Scheme name cannot be empty")

    return name


def get_scheme_path(scheme: str) -> Path:
    name = normalize_scheme(scheme)
    path = SCHEME_DIR / f"base2tone-{name}.yml"

    if not path.is_file():
        raise ThemeError(f"Scheme not found: {path}")

    return path


def list_schemes() -> tuple[str, ...]:
    if not SCHEME_DIR.is_dir():
        raise ThemeError(
            f"Scheme directory not found: {SCHEME_DIR}"
        )

    schemes = tuple(
        sorted(
            path.stem.removeprefix("base2tone-")
            for path in SCHEME_DIR.glob("base2tone-*.yml")
        )
    )

    if not schemes:
        raise ThemeError(
            f"No Base2Tone schemes found beneath {SCHEME_DIR}"
        )

    return schemes


def load_palette(scheme: str) -> Palette:
    name = normalize_scheme(scheme)
    path = get_scheme_path(scheme)
    text = path.read_text(encoding="utf-8")

    colors: dict[str, str] = {}

    for bank, index, value in PALETTE_PATTERN.findall(text):
        coordinate = f"{bank}{index}"

        if coordinate in colors:
            raise ThemeError(
                f"Duplicate coordinate {coordinate} in {path}"
            )

        # Templates control whether their native format requires "#".
        colors[coordinate] = value.lower()

    missing = [
        coordinate
        for coordinate in EXPECTED_COORDINATES
        if coordinate not in colors
    ]

    if missing:
        raise ThemeError(
            f"Missing coordinates in {path}: {', '.join(missing)}"
        )

    if len(colors) != len(EXPECTED_COORDINATES):
        raise ThemeError(
            f"Expected 32 coordinates in {path}; found {len(colors)}"
        )

    return Palette(
        name=name,
        source=path,
        colors=colors,
    )


def safe_relative_path(
    value: object,
    *,
    field: str,
    manifest: Path,
) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ThemeError(
            f"{manifest}: {field!r} must be a non-empty string"
        )

    path = Path(value)

    if path.is_absolute() or ".." in path.parts:
        raise ThemeError(
            f"{manifest}: {field!r} must be a safe relative path"
        )

    return path


def load_module(manifest: Path) -> ToolModule:
    try:
        with manifest.open("rb") as file:
            data = tomllib.load(file)
    except tomllib.TOMLDecodeError as error:
        raise ThemeError(
            f"Invalid TOML in {manifest}: {error}"
        ) from error

    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        raise ThemeError(
            f"{manifest}: 'name' must be a non-empty string"
        )

    name = name.strip()

    if name != manifest.parent.name:
        raise ThemeError(
            f"{manifest}: module name {name!r} must match "
            f"directory name {manifest.parent.name!r}"
        )

    template_relative = safe_relative_path(
        data.get("template"),
        field="template",
        manifest=manifest,
    )

    output_relative = safe_relative_path(
        data.get("output"),
        field="output",
        manifest=manifest,
    )

    template = manifest.parent / template_relative

    if not template.is_file():
        raise ThemeError(
            f"{manifest}: template not found: {template}"
        )

    postprocess_value = data.get("postprocess")
    postprocess: Path | None = None

    if postprocess_value is not None:
        postprocess_relative = safe_relative_path(
            postprocess_value,
            field="postprocess",
            manifest=manifest,
        )

        postprocess = manifest.parent / postprocess_relative

        if not postprocess.is_file():
            raise ThemeError(
                f"{manifest}: postprocess hook not found: {postprocess}"
            )

    return ToolModule(
        name=name,
        directory=manifest.parent,
        template=template,
        output=output_relative,
        manifest=manifest,
        postprocess=postprocess,
    )


def discover_modules() -> tuple[ToolModule, ...]:
    if not TOOLS_DIR.is_dir():
        raise ThemeError(
            f"Tool module directory not found: {TOOLS_DIR}"
        )

    manifests = sorted(TOOLS_DIR.glob("*/tool.toml"))

    if not manifests:
        raise ThemeError(
            f"No tool manifests found beneath {TOOLS_DIR}"
        )

    modules = tuple(load_module(path) for path in manifests)

    names = [module.name for module in modules]

    if len(names) != len(set(names)):
        raise ThemeError("Duplicate tool module names found")

    outputs = [module.output for module in modules]

    if len(outputs) != len(set(outputs)):
        raise ThemeError("Duplicate generated output paths found")

    return modules


def render_template(
    template: Path,
    palette: Palette,
) -> str:
    text = template.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        coordinate = match.group(1)
        return palette.colors[coordinate]

    rendered = PLACEHOLDER_PATTERN.sub(replace, text)

    unresolved = sorted(
        set(ANY_PLACEHOLDER_PATTERN.findall(rendered))
    )

    if unresolved:
        formatted = ", ".join(
            f"{{{{{value}}}}}"
            for value in unresolved
        )

        raise ThemeError(
            f"Unknown placeholders in {template}: {formatted}"
        )

    return rendered


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def run_postprocess(
    module: ToolModule,
    rendered_output: Path,
    destination: Path,
) -> tuple[Path, ...]:
    if module.postprocess is None:
        return ()

    module_name = f"b2t_tool_{module.name}_postprocess"

    spec = importlib.util.spec_from_file_location(
        module_name,
        module.postprocess,
    )

    if spec is None or spec.loader is None:
        raise ThemeError(
            f"Could not load postprocess hook: {module.postprocess}"
        )

    hook_module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(hook_module)
    except Exception as error:
        raise ThemeError(
            f"Could not import postprocess hook "
            f"{module.postprocess}: {error}"
        ) from error

    build_hook = getattr(hook_module, "build", None)

    if not callable(build_hook):
        raise ThemeError(
            f"{module.postprocess}: expected callable build()"
        )

    try:
        result = build_hook(rendered_output, destination)
    except Exception as error:
        raise ThemeError(
            f"Postprocess failed for {module.name}: {error}"
        ) from error

    if result is None:
        return ()

    if not isinstance(result, (tuple, list)):
        raise ThemeError(
            f"{module.postprocess}: build() must return "
            "a tuple or list of relative output paths"
        )

    outputs: list[Path] = []

    for value in result:
        relative = safe_relative_path(
            str(value),
            field="postprocess output",
            manifest=module.manifest,
        )

        output = destination / relative

        if not output.is_file():
            raise ThemeError(
                f"{module.postprocess}: declared output "
                f"was not created: {output}"
            )

        outputs.append(output)

    return tuple(outputs)


def render_modules(
    palette: Palette,
    modules: tuple[ToolModule, ...],
    destination: Path,
) -> tuple[Path, ...]:
    outputs: list[Path] = []

    for module in modules:
        output = destination / module.output
        rendered = render_template(module.template, palette)

        write_atomic(output, rendered)
        outputs.append(output)

        outputs.extend(
            run_postprocess(
                module,
                output,
                destination,
            )
        )

    write_atomic(destination / "scheme", f"{palette.name}\n")
    outputs.append(destination / "scheme")

    return tuple(outputs)


def build_active(scheme: str) -> BuildResult:
    palette = load_palette(scheme)
    modules = discover_modules()

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    temporary = Path(
        tempfile.mkdtemp(
            prefix=".build-",
            dir=GENERATED_DIR,
        )
    )

    previous = GENERATED_DIR / ".previous"
    current_moved = False

    try:
        temporary_outputs = render_modules(
            palette,
            modules,
            temporary,
        )

        if previous.exists():
            shutil.rmtree(previous)

        if CURRENT_DIR.exists():
            CURRENT_DIR.replace(previous)
            current_moved = True

        temporary.replace(CURRENT_DIR)

        if previous.exists():
            shutil.rmtree(previous)

    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)

        if (
            current_moved
            and not CURRENT_DIR.exists()
            and previous.exists()
        ):
            previous.replace(CURRENT_DIR)

        raise

    outputs = tuple(
        CURRENT_DIR / output.relative_to(temporary)
        for output in temporary_outputs
    )

    return BuildResult(
        palette=palette,
        modules=modules,
        outputs=outputs,
    )
