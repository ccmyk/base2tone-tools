# Architecture

## Purpose

Base2Tone Tools converts an upstream Base2Tone scheme into native theme or
configuration files for command-line applications.

The project preserves the original 32-coordinate Base2Tone vocabulary:

    A0..A7
    B0..B7
    C0..C7
    D0..D7

It does not introduce a global semantic color layer.

## Data flow

    upstream Base2Tone scheme YAML
            ↓
    parse all 32 coordinates
            ↓
    validate the palette
            ↓
    render one template per tool
            ↓
    write files under generated/
            ↓
    optionally install selected outputs

## Source of truth

The canonical palette source is:

    vendor/Base2Tone/db/schemes/base2tone-<scheme>.yml

Generated application themes are not palette sources.

Templates may use upstream application-specific Base2Tone projects as mapping
references, but those projects do not replace the core scheme YAML.

## Direct-coordinate model

Templates use the original coordinates directly:

    {{A0}}
    {{A1}}
    {{B4}}
    {{C7}}
    {{D5}}

A template should visibly show the relationship between a tool-native field
and a Base2Tone coordinate.

Example:

    filekinds:
      # Ordinary files remain readable without becoming visually dominant.
      normal:
        foreground: "{{A6}}"

      # Directories require a visible navigational distinction.
      directory:
        foreground: "{{B4}}"

The mapping belongs to the tool template.

The compiler does not translate through intermediate names such as:

    background
    navigation
    success
    warning
    danger
    accent

## Compiler responsibilities

The compiler will:

1. Locate a requested Base2Tone scheme.
2. Parse `baseA0..baseD7`.
3. Verify that all 32 coordinates exist.
4. Normalize values into hexadecimal strings.
5. Replace direct coordinate placeholders in templates.
6. Write generated files beneath `generated/`.
7. Report generated files and validation errors.

The compiler will not:

- decide universal semantic meanings for B and D;
- modify dotfiles during ordinary compilation;
- silently overwrite application configuration;
- infer colors from previously generated themes;
- hand-edit generated output.

## Template responsibilities

Each template will:

- use the target tool's native schema;
- map native fields directly to Base2Tone coordinates;
- include comments explaining important assignments;
- document unusual contrast or hierarchy decisions;
- avoid unnecessary assignments where the application's default is preferable;
- remain independently readable without inspecting compiler source.

## Compilation and installation

Compilation and installation are separate operations.

Compilation writes only beneath:

    generated/

Installation may later:

- copy generated files;
- create symbolic links;
- update a clearly marked generated section;
- print manual integration instructions.

Installation must be explicit.

## Generated output layout

Generated files will be grouped by scheme:

    generated/
    └── motel/
        ├── eza.yml
        ├── vivid.yml
        ├── fzf.zsh
        └── ...

This permits multiple schemes to be generated and compared simultaneously.

A later active-theme mechanism may point applications at one generated scheme,
but it is not part of the initial compiler.

## Project layout

    base2tone-tools/
    ├── bin/
    │   └── b2t-theme
    ├── docs/
    │   ├── ARCHITECTURE.md
    │   ├── PALETTE.md
    │   └── TOOLS.md
    ├── generated/
    ├── scripts/
    │   └── analyze-palettes.py
    ├── templates/
    └── vendor/
        └── Base2Tone/

## Implementation phases

### Phase 1: Scaffold and documentation

- Create the repository.
- Add the upstream Base2Tone source.
- Define project boundaries.
- Document the palette and tool roadmap.

### Phase 2: Compiler foundation

- Parse a scheme.
- Validate all 32 coordinates.
- Render direct placeholders.
- Generate files without installing them.

### Phase 3: Palette analysis

- Compare lightness across all coordinates.
- Compare hue relationships between banks.
- identify irregular ramps and scheme-specific exceptions.
- Produce readable analysis reports.

### Phase 4: Filesystem themes

- eza
- vivid
- `LS_COLORS` integration

### Phase 5: Shell interaction themes

- fzf
- fast-syntax-highlighting
- Yazi

### Phase 6: Terminal workspace themes

- tmux
- Zellij
- Starship

### Phase 7: Git and document tools

- Lazygit
- Delta
- Glow
- bat

### Phase 8: Monitoring and information tools

- Bottom
- Fastfetch

### Phase 9: Installation lifecycle

- install
- uninstall
- status
- dry-run
