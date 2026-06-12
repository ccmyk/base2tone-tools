# Yazi

This module owns the complete Base2Tone theme for Yazi.

## Files

- `template.toml` contains deliberately maintained interface and filetype
  mappings.
- `icons.toml` contains the complete shipped Yazi icon database with direct
  Base2Tone coordinates.
- `tool.toml` declares both ordered template parts, the output, and validator.
- `validate.py` checks the combined generated theme.

## Manifest

    name = "yazi"
    template = "template.toml"
    append = ["icons.toml"]
    output = "yazi/theme.toml"
    validator = "validate.py"

## Output

Both maintained template parts compile into one file:

    generated/current/yazi/theme.toml

No separate icon file is installed.

## Interface template

`template.toml` contains the readable portion of the theme:

- application and manager styling;
- tabs and modes;
- status and permissions;
- dialogs and notifications;
- picker, input, and completion;
- task manager and help;
- filetype rules.

Every tool-native field visibly maps to an original Base2Tone coordinate.

## Complete icons

`icons.toml` preserves all shipped selectors and glyphs for:

- glob rules;
- directories;
- named files;
- extensions;
- conditional rules.

Yazi requires an individual color on each icon rule when replacing the complete
icon table. Keeping those rules in a separate fragment prevents the readable
interface template from being buried beneath hundreds of repetitive entries.

## Validation

The validator checks:

- TOML syntax;
- required interface sections;
- required manager fields;
- filetype rules;
- every icon group;
- minimum icon-table sizes;
- individual icon-rule structure;
- hexadecimal color syntax;
- isolated loading through `yazi --debug`.
