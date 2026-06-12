# fast-syntax-highlighting

This module owns the Base2Tone theme for fast-syntax-highlighting.

## Files

- `template.ini` maps Fast Syntax Highlighting style fields directly to
  Base2Tone coordinates.
- `tool.toml` declares the template, output, and validator.
- `validate.py` checks the generated INI structure, expected fields, color
  syntax, background syntax, and supported text styles.

## Manifest

    name = "fsh"
    template = "template.ini"
    output = "fsh/base2tone.ini"
    validator = "validate.py"

## Output

    generated/current/fsh/base2tone.ini

## Mapping format

Each Fast Syntax Highlighting field occupies its own line:

    command            = #{{B5}},bold
    path               = #{{D4}}
    variable           = #{{C5}}
    unknown-token      = #{{B2}},bold

This keeps every native field and Base2Tone coordinate directly adjacent.

## Theme format

The output is a complete Fast Syntax Highlighting INI theme rather than an
overlay.

Foreground colors use:

    #RRGGBB

Background colors use:

    bg:#RRGGBB

Additional styles may follow as comma-separated values:

    #RRGGBB,bold
    #RRGGBB,underline

## Installation

A later apply operation will install the generated file beneath the user's FSH
configuration directory.

The intended activation form is:

    fast-theme XDG:base2tone

Installation and activation are intentionally separate from ordinary builds.

## Validation

The project validator does not alter the user's active Fast Syntax Highlighting
theme.

It validates the generated INI structure and the same style-token forms
accepted by Fast Syntax Highlighting.
