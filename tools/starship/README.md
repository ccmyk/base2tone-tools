# Starship

This module generates the Base2Tone custom color palette used by the personal
Starship prompt configuration.

## Files

- `template.toml` maps every Starship palette entry directly to a Base2Tone
  coordinate.
- `tool.toml` declares the generated output and validator.
- `validate.py` checks the palette and loads it through Starship.

## Output

    generated/current/starship/palette.toml

## Coordinate model

Starship references the same coordinate names used by the other modules:

    A0
    A1
    B4
    C7
    D6

It does not use a second naming system such as:

    b2t_a0
    b2t_b4
    b2t_d6

The palette table remains named `b2t` because Starship requires an active
palette name:

    palette = "b2t"

The entries within that palette retain the original Base2Tone coordinate names.

## Installation

The generated palette fragment is spliced into the personal Starship
configuration during apply:

    b2t-theme apply <scheme> --module starship

The install step replaces only the marked palette block:

    # BEGIN generated Base2Tone Starship palette
    ...
    # END generated Base2Tone Starship palette

Reload the shell after apply so Starship reads the updated palette.

## Configuration boundary

The personal Starship configuration owns:

- prompt order;
- module formats;
- symbols;
- detection rules;
- enabled and disabled modules.

This module owns only:

    [palettes.b2t]

Starship does not receive duplicated prompt behavior from this project.

## Validation

Validation confirms:

- exactly 32 coordinates are present;
- every coordinate is named `A0` through `D7`;
- every value is a six-digit hexadecimal color;
- no placeholders remain;
- Starship accepts a configuration using the generated palette.
