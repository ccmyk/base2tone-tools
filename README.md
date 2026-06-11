# Base2Tone Tools

A template-based generator for applying Base2Tone’s original 32-coordinate
palette to command-line tools and terminal applications.

## Design principles

- Preserve Base2Tone’s original coordinate names:
  `A0..A7`, `B0..B7`, `C0..C7`, and `D0..D7`.
- Do not create a global semantic color layer.
- Do not replace the coordinates with aliases such as `background`, `accent`,
  `success`, `warning`, or `danger`.
- Map every tool-native field directly to a Base2Tone coordinate.
- Keep those coordinate assignments visible inside each tool template.
- Use comments in each template to explain why a coordinate was selected.
- Document scheme-specific exceptions where differences in hue, saturation,
  or lightness affect a mapping.
- Keep generated files disposable and reproducible.
- Separate compilation from installation.
- Do not modify a user’s dotfiles merely by compiling templates.

## Palette model

Each Base2Tone scheme provides four banks with eight coordinates each:

    A0 A1 A2 A3 A4 A5 A6 A7
    B0 B1 B2 B3 B4 B5 B6 B7
    C0 C1 C2 C3 C4 C5 C6 C7
    D0 D1 D2 D3 D4 D5 D6 D7

The coordinate names identify palette positions. They are not universal
semantic labels.

The broad tendencies found across Base2Tone dark schemes are:

- The A bank usually contains dark structural and lower-emphasis values.
- The C bank usually contains the lightest readable values.
- The B and D banks are chromatic families.
- Each numbered stop represents a position within its own bank.
- Hue distance between B and D varies significantly between schemes.
- Lightness progression is broadly structured but not mathematically identical
  in every scheme.
- Some schemes deliberately compress, reorder, or emphasize parts of a ramp.

These tendencies guide tool-specific mappings, but they do not create a second
public variable system.

## Data flow

    Base2Tone scheme YAML
            ↓
    load A0..A7, B0..B7, C0..C7, D0..D7
            ↓
    validate that all 32 coordinates exist
            ↓
    substitute coordinates into one template per tool
            ↓
    write native generated configuration files
            ↓
    optionally install selected outputs

## Template model

Each template contains the target tool’s native fields and direct Base2Tone
coordinate references.

For example:

    filekinds:
      # Ordinary files should remain readable without becoming dominant.
      normal:
        foreground: "{{A6}}"

      # Directories are navigational objects and receive a chromatic distinction.
      directory:
        foreground: "{{B4}}"

This makes the mapping visible:

    tool-native field
            ↓
    direct Base2Tone coordinate
            ↓
    generated hexadecimal value

There is no intermediate global role such as:

    directory -> navigation -> accent -> B4

Instead, the template states the actual relationship:

    eza.filekinds.directory -> B4

The nearby comment explains why.

## Project boundaries

The compiler is responsible for:

1. Finding a Base2Tone scheme.
2. Parsing all 32 coordinates.
3. Rejecting incomplete or malformed schemes.
4. Rendering tool templates.
5. Writing generated files.
6. Reporting what was produced.

The compiler is not responsible for deciding that one coordinate universally
means success, danger, navigation, or another semantic category.

Those decisions belong inside each tool template because different tools have
different visual structures and requirements.

## Compilation and installation

Compilation writes only into this repository’s generated output directory:

    generated/

Compilation must not overwrite application configuration files.

Installation is a separate operation that may:

- copy a generated file;
- create a symlink;
- update a clearly marked generated block;
- print manual integration instructions.

This separation allows templates to be developed and tested safely.

## Planned project structure

    base2tone-tools/
    ├── bin/
    │   └── b2t-theme
    ├── docs/
    │   ├── ARCHITECTURE.md
    │   ├── PALETTE.md
    │   └── TOOLS.md
    ├── generated/
    │   └── .gitkeep
    ├── scripts/
    │   └── analyze-palettes.py
    ├── templates/
    │   ├── eza.yml
    │   ├── vivid.yml
    │   ├── fzf.zsh
    │   └── ...
    └── vendor/
        └── Base2Tone/

## Planned implementation order

1. Project structure and documentation
2. Palette loader
3. Template renderer
4. Palette validation
5. Palette-analysis utilities
6. eza
7. vivid and `LS_COLORS`
8. fzf
9. fast-syntax-highlighting
10. Yazi
11. tmux
12. Zellij
13. Starship
14. Lazygit
15. Delta
16. Glow
17. Bottom
18. Fastfetch
19. bat integration
20. Installation and removal commands

## Initial tool pair

The first tool templates will be eza and vivid.

They are useful together because both describe files and filesystem states, but
they produce different outputs:

- eza consumes its own native YAML theme.
- vivid compiles a YAML theme into the `LS_COLORS` environment variable.
- `LS_COLORS` can then affect multiple compatible command-line tools.

Implementing both first will test whether direct `A0..D7` mappings remain clear
across related tools without introducing global semantic aliases.

## Source of truth

The canonical palette source is the upstream Base2Tone scheme collection:

    vendor/Base2Tone/db/schemes/base2tone-<scheme>.yml

Generated application themes are never used as the palette source.

## Status

This project is being rebuilt from the beginning around direct Base2Tone
coordinate mappings and tool-specific templates.
