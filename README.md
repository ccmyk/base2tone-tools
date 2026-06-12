# Base2Tone Tools

Base2Tone Tools builds native themes and configuration fragments for
command-line applications from the original 32-coordinate Base2Tone schemes.

The project preserves the upstream coordinate system directly:

    A0 A1 A2 A3 A4 A5 A6 A7
    B0 B1 B2 B3 B4 B5 B6 B7
    C0 C1 C2 C3 C4 C5 C6 C7
    D0 D1 D2 D3 D4 D5 D6 D7

It does not introduce a shared semantic color dictionary.

Tool templates visibly assign Base2Tone coordinates to tool-native fields.

## Architecture

The project uses:

- one thin command-line launcher;
- one shared palette compiler;
- one self-contained module per supported tool;
- one active generated output set.

    Base2Tone scheme
            ↓
    bin/b2t-theme
            ↓
    lib/compiler.py
            ↓
    tools/*/tool.toml
            ↓
    tool-owned native templates
            ↓
    generated/current/

Each tool module owns its color mapping, documentation, generated output path,
and any exceptional validation or post-processing behavior.

## Project structure

    base2tone-tools/
    ├── bin/
    │   └── b2t-theme
    ├── lib/
    │   └── compiler.py
    ├── tools/
    │   ├── eza/
    │   │   ├── README.md
    │   │   ├── template.yml
    │   │   └── tool.toml
    │   └── ...
    ├── generated/
    │   └── current/
    ├── docs/
    │   ├── ARCHITECTURE.md
    │   ├── PALETTE.md
    │   └── TOOLS.md
    └── vendor/
        └── Base2Tone/

## Source of truth

Palette data comes from:

    vendor/Base2Tone/db/schemes/base2tone-<scheme>.yml

Each scheme must contain exactly 32 coordinates:

    baseA0..baseA7
    baseB0..baseB7
    baseC0..baseC7
    baseD0..baseD7

## Tool modules

A normal module contains:

    tools/<tool>/
    ├── README.md
    ├── template.<native-extension>
    └── tool.toml

Example manifest:

    name = "eza"
    template = "template.yml"
    output = "eza/theme.yml"

The manifest contains operational metadata only.

Color assignments remain visible in the native template:

    directory:
      foreground: "#{{B4}}"

The compiler substitutes `{{B4}}` with the selected scheme's bare six-digit
hexadecimal value. The template supplies any required `#`, escape sequence, or
other surrounding syntax.

## Generated output

Normal builds retain only one active output set:

    generated/current/

Switching schemes replaces that directory only after the complete build
succeeds.

Testing all schemes uses temporary directories and does not retain hundreds of
generated files.

## Commands

Implemented commands:

    b2t-theme list
    b2t-theme validate <scheme>
    b2t-theme build <scheme>
    b2t-theme test

Planned lifecycle commands:

    b2t-theme apply <scheme>
    b2t-theme current
    b2t-theme status

## Dotfiles integration

This project remains separate from the dotfiles repository:

    ~/development/base2tone-tools
        compiler, modules, tests, and upstream Base2Tone data

    ~/.dotfiles
        installed active output used by applications

A later explicit `apply` operation will build and validate everything before
installing one active theme set into the dotfiles repository.

Ordinary builds will not modify dotfiles.
