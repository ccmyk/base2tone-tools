from __future__ import annotations

import importlib.util
import os
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

SCHEME_PLACEHOLDER_PATTERN = re.compile(
    r"\{\{\s*SCHEME\s*\}\}"
)

ANY_PLACEHOLDER_PATTERN = re.compile(
    r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}"
)


class ThemeError(Exception):
    """Raised for expected scheme, module, or rendering errors."""


@dataclass(frozen=True)
class Palette:
    name: str
    source: Path
    colors: dict[str, str]


@dataclass(frozen=True)
class InstallSpec:
    source: Path
    target: Path
    mode: str
    begin_marker: str | None = None
    end_marker: str | None = None


@dataclass(frozen=True)
class ToolModule:
    name: str
    directory: Path
    template: Path
    append_templates: tuple[Path, ...]
    output: Path
    manifest: Path
    postprocess: Path | None
    validator: Path | None
    installs: tuple[InstallSpec, ...]


@dataclass(frozen=True)
class BuildResult:
    palette: Palette
    modules: tuple[ToolModule, ...]
    outputs: tuple[Path, ...]


@dataclass(frozen=True)
class ApplyResult:
    palette: Palette
    modules: tuple[ToolModule, ...]
    installed: tuple[Path, ...]


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


def load_one_install_spec(
    install_value: dict[str, object],
    *,
    manifest: Path,
    index: int,
    default_source: Path,
) -> InstallSpec:
    prefix = "install" if index == 0 else f"install[{index}]"

    source_value = install_value.get("source")

    if source_value is None:
        source_relative = default_source
    else:
        source_relative = safe_relative_path(
            source_value,
            field=f"{prefix}.source",
            manifest=manifest,
        )

    target_relative = safe_relative_path(
        install_value.get("target"),
        field=f"{prefix}.target",
        manifest=manifest,
    )

    mode = install_value.get("mode")

    if not isinstance(mode, str) or not mode.strip():
        raise ThemeError(
            f"{manifest}: {prefix}.mode must be a non-empty string"
        )

    mode = mode.strip()

    if mode not in {"symlink", "palette-block"}:
        raise ThemeError(
            f"{manifest}: unsupported install mode {mode!r}"
        )

    begin_marker = install_value.get("begin")
    end_marker = install_value.get("end")

    if mode == "palette-block":
        if (
            not isinstance(begin_marker, str)
            or not begin_marker.strip()
            or not isinstance(end_marker, str)
            or not end_marker.strip()
        ):
            raise ThemeError(
                f"{manifest}: palette-block install requires "
                f"{prefix}.begin and {prefix}.end markers"
            )

        return InstallSpec(
            source=source_relative,
            target=target_relative,
            mode=mode,
            begin_marker=begin_marker.strip(),
            end_marker=end_marker.strip(),
        )

    if begin_marker is not None or end_marker is not None:
        raise ThemeError(
            f"{manifest}: install markers are only valid for "
            "palette-block installs"
        )

    return InstallSpec(
        source=source_relative,
        target=target_relative,
        mode=mode,
    )


def load_install_specs(
    data: dict[str, object],
    *,
    manifest: Path,
    default_source: Path,
) -> tuple[InstallSpec, ...]:
    install_value = data.get("install")

    if install_value is None:
        return ()

    if isinstance(install_value, dict):
        return (
            load_one_install_spec(
                install_value,
                manifest=manifest,
                index=0,
                default_source=default_source,
            ),
        )

    if isinstance(install_value, list):
        specs: list[InstallSpec] = []

        for index, value in enumerate(install_value):
            if not isinstance(value, dict):
                raise ThemeError(
                    f"{manifest}: install[{index}] must be a table"
                )

            specs.append(
                load_one_install_spec(
                    value,
                    manifest=manifest,
                    index=index,
                    default_source=default_source,
                )
            )

        return tuple(specs)

    raise ThemeError(
        f"{manifest}: 'install' must be a table or array of tables"
    )


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

    append_value = data.get("append", [])

    if not isinstance(append_value, list):
        raise ThemeError(
            f"{manifest}: 'append' must be an array of relative paths"
        )

    append_templates: list[Path] = []

    for index, value in enumerate(append_value):
        append_relative = safe_relative_path(
            value,
            field=f"append[{index}]",
            manifest=manifest,
        )

        append_template = manifest.parent / append_relative

        if not append_template.is_file():
            raise ThemeError(
                f"{manifest}: appended template not found: "
                f"{append_template}"
            )

        append_templates.append(append_template)

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

    validator_value = data.get("validator")
    validator: Path | None = None

    if validator_value is not None:
        validator_relative = safe_relative_path(
            validator_value,
            field="validator",
            manifest=manifest,
        )

        validator = manifest.parent / validator_relative

        if not validator.is_file():
            raise ThemeError(
                f"{manifest}: validator hook not found: {validator}"
            )

    installs = load_install_specs(
        data,
        manifest=manifest,
        default_source=output_relative,
    )

    return ToolModule(
        name=name,
        directory=manifest.parent,
        template=template,
        append_templates=tuple(append_templates),
        output=output_relative,
        manifest=manifest,
        postprocess=postprocess,
        validator=validator,
        installs=installs,
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
    rendered = SCHEME_PLACEHOLDER_PATTERN.sub(
        palette.name,
        rendered,
    )

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


def run_validator(
    module: ToolModule,
    rendered_output: Path,
    destination: Path,
) -> None:
    if module.validator is None:
        return

    module_name = f"b2t_tool_{module.name}_validator"

    spec = importlib.util.spec_from_file_location(
        module_name,
        module.validator,
    )

    if spec is None or spec.loader is None:
        raise ThemeError(
            f"Could not load validator hook: {module.validator}"
        )

    validator_module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(validator_module)
    except Exception as error:
        raise ThemeError(
            f"Could not import validator hook "
            f"{module.validator}: {error}"
        ) from error

    validate_hook = getattr(validator_module, "validate", None)

    if not callable(validate_hook):
        raise ThemeError(
            f"{module.validator}: expected callable validate()"
        )

    try:
        validate_hook(rendered_output, destination)
    except Exception as error:
        raise ThemeError(
            f"Validation failed for {module.name}: {error}"
        ) from error


def render_modules(
    palette: Palette,
    modules: tuple[ToolModule, ...],
    destination: Path,
) -> tuple[Path, ...]:
    outputs: list[Path] = []

    for module in modules:
        output = destination / module.output

        rendered_parts = [
            render_template(module.template, palette)
        ]

        rendered_parts.extend(
            render_template(template, palette)
            for template in module.append_templates
        )

        rendered = "\n\n".join(
            part.rstrip("\n")
            for part in rendered_parts
        ) + "\n"

        write_atomic(output, rendered)
        outputs.append(output)

        outputs.extend(
            run_postprocess(
                module,
                output,
                destination,
            )
        )

        run_validator(
            module,
            output,
            destination,
        )

    write_atomic(destination / "scheme", f"{palette.name}\n")
    outputs.append(destination / "scheme")

    return tuple(outputs)


def test_all_schemes() -> tuple[str, ...]:
    modules = discover_modules()
    passed: list[str] = []

    with tempfile.TemporaryDirectory(
        prefix="base2tone-tools-test-"
    ) as temporary_directory:
        temporary_root = Path(temporary_directory)

        for scheme in list_schemes():
            palette = load_palette(scheme)
            destination = temporary_root / palette.name

            render_modules(
                palette,
                modules,
                destination,
            )

            passed.append(palette.name)

    return tuple(passed)


def default_install_root() -> Path:
    override = os.environ.get("B2T_INSTALL_ROOT")

    if override:
        return Path(override).expanduser()

    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")

    if xdg_config_home:
        return Path(xdg_config_home).expanduser()

    return Path.home() / ".config"


def replace_palette_block(
    target_text: str,
    palette_text: str,
    *,
    begin_marker: str,
    end_marker: str,
    target: Path,
) -> str:
    begin_index = target_text.find(begin_marker)

    if begin_index == -1:
        raise ThemeError(
            f"{target}: missing palette begin marker: {begin_marker}"
        )

    end_index = target_text.find(end_marker, begin_index)

    if end_index == -1:
        raise ThemeError(
            f"{target}: missing palette end marker: {end_marker}"
        )

    end_index += len(end_marker)

    if end_index < len(target_text) and target_text[end_index] == "\n":
        end_index += 1

    return (
        target_text[:begin_index]
        + palette_text.rstrip("\n")
        + "\n"
        + target_text[end_index:]
    )


def install_module_output(
    module: ToolModule,
    install: InstallSpec,
    *,
    generated_root: Path,
    install_root: Path,
) -> Path:
    generated_output = generated_root / install.source

    if not generated_output.is_file():
        raise ThemeError(
            f"Generated install source not found for {module.name}: "
            f"{generated_output}"
        )

    destination = install_root / install.target
    destination.parent.mkdir(parents=True, exist_ok=True)

    if install.mode == "symlink":
        if destination.exists() or destination.is_symlink():
            if destination.is_symlink():
                destination.unlink()
            elif destination.is_file():
                destination.unlink()
            else:
                raise ThemeError(
                    f"install target is not a file: {destination}"
                )

        destination.symlink_to(generated_output)
        return destination

    palette_text = generated_output.read_text(encoding="utf-8")

    if destination.is_file():
        target_text = destination.read_text(encoding="utf-8")
    elif not destination.exists():
        raise ThemeError(
            f"palette-block install requires an existing target: "
            f"{destination}"
        )
    else:
        raise ThemeError(
            f"install target is not a regular file: {destination}"
        )

    updated = replace_palette_block(
        target_text,
        palette_text,
        begin_marker=install.begin_marker or "",
        end_marker=install.end_marker or "",
        target=destination,
    )

    write_atomic(destination, updated)
    return destination


def apply_active(
    scheme: str,
    *,
    install_root: Path | None = None,
    modules: tuple[str, ...] | None = None,
) -> ApplyResult:
    result = build_active(scheme)
    root = install_root or default_install_root()
    root.mkdir(parents=True, exist_ok=True)

    selected = set(modules) if modules is not None else None
    installed: list[Path] = []

    for module in result.modules:
        if selected is not None and module.name not in selected:
            continue

        for install in module.installs:
            installed.append(
                install_module_output(
                    module,
                    install,
                    generated_root=CURRENT_DIR,
                    install_root=root,
                )
            )

    return ApplyResult(
        palette=result.palette,
        modules=result.modules,
        installed=tuple(installed),
    )


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
