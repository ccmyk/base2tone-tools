# Fastfetch

This module owns the complete generated Fastfetch configuration.

## Files

- `template.jsonc` preserves the user's Fastfetch layout and module list.
- `tool.toml` declares the generated output and validator.
- `validate.py` verifies the rendered configuration with Fastfetch.

## Output

    generated/current/fastfetch/config.jsonc

## Base2Tone hierarchy

The interface uses direct Base2Tone coordinates:

- `B4` for keys and navigation labels;
- `C6` for the title;
- `C5` for primary information;
- `A3` for separators and remaining bar segments;
- `A4` for bar borders;
- `D4` for active percentage bars;
- `D6` and `B4` for elevated percentage states.

The module does not alter the selected Fastfetch modules, system commands,
storage paths, key widths, or overall layout.

## Validation

The validator loads the generated configuration with Fastfetch while
temporarily overriding the module structure to `title`. This verifies parsing
without repeatedly executing cache, Docker, storage, and mount commands during
the all-scheme test.
