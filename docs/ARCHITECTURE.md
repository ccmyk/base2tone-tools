# Architecture

## Core design

Base2Tone Tools uses three layers:

    thin launcher
          ↓
    shared compiler
          ↓
    independent tool modules

The layers have deliberately narrow responsibilities.

## Data flow

    vendor/Base2Tone scheme YAML
                ↓
    parse and validate A0..D7
                ↓
    discover tools/*/tool.toml
                ↓
    render each module's native template
                ↓
    validate and post-process when required
                ↓
    generated/current/

Only the active generated scheme is retained during normal operation.

## Thin launcher

The launcher lives at:

    bin/b2t-theme

It is responsible for:

- command-line argument parsing;
- selecting the requested operation;
- calling shared compiler functions;
- reporting success and errors.

It should not contain:

- tool-specific color mappings;
- eza-specific configuration construction;
- vivid-specific LS_COLORS mappings;
- global semantic aliases.

## Shared compiler

The shared compiler lives at:

    lib/compiler.py

It is responsible for:

1. Locating an upstream Base2Tone scheme.
2. Normalizing scheme names.
3. Parsing all 32 coordinates.
4. Rejecting duplicate, missing, or invalid coordinates.
5. Reading tool manifests.
6. Replacing direct coordinate placeholders.
7. Writing generated files atomically.
8. Building into temporary storage before replacing the active output.

The compiler treats coordinates as identifiers, not semantic roles.

## Tool modules

Each supported tool owns one directory:

    tools/<name>/

A basic module contains:

    README.md
    template.<native-extension>
    tool.toml

The template owns the tool-specific color decisions.

The manifest owns operational metadata only.

Example:

    name = "eza"
    template = "template.yml"
    output = "eza/theme.yml"

A module may later include narrowly scoped hooks:

    build.py
    validate.py
    install.py
    reload.py

Hooks are added only when the tool genuinely requires behavior beyond direct
template substitution.

## Direct-coordinate model

Templates use the original Base2Tone coordinates:

    {{A0}}
    {{B4}}
    {{C6}}
    {{D5}}

The compiler supplies bare six-digit hexadecimal values.

A template requiring a leading number sign writes:

    foreground: "#{{B4}}"

A format requiring a bare hexadecimal value writes:

    color: "{{B4}}"

This keeps output syntax under the control of the native template.

## No semantic layer

The project will not create shared aliases such as:

    background = A0
    navigation = B4
    success = D4
    warning = D6
    danger = B2

Those meanings are not guaranteed across all Base2Tone schemes.

A coordinate may be chosen for a local purpose inside one tool, but that local
decision does not become a global definition.

## Generated output

Normal output is limited to:

    generated/current/

Example:

    generated/current/
    ├── scheme
    ├── eza/
    │   └── theme.yml
    ├── vivid/
    │   ├── theme.yml
    │   └── ls-colors.zsh
    └── ...

The `scheme` file records the active scheme name.

The entire replacement build must succeed before `generated/current/` changes.

## All-scheme testing

The command:

    b2t-theme test

tests every scheme using temporary directories:

    /tmp/base2tone-tools-.../

The test operation should:

1. Render each scheme.
2. Run each available module validator.
3. Report pass or failure.
4. Remove temporary output.

It should not create a permanent scheme-by-tool output matrix.

## Dotfiles boundary

The development project is not a runtime dependency of the dotfiles repository.

A future explicit apply operation will:

1. Render into temporary storage.
2. Validate every enabled module.
3. Stop without touching dotfiles on any failure.
4. Install one active output set into `~/.dotfiles`.
5. Run optional reload hooks.
6. Record the active scheme.

Ordinary `build` operations remain local to this project.

## Vendored dependencies

The only current vendored dependency is:

    vendor/Base2Tone

It is vendored because its scheme files are direct compiler input.

Applications such as eza and vivid are installed consumers and validators.
Their complete source repositories do not need to be vendored.
