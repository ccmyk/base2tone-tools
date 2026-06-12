# eza

This module owns the Base2Tone integration for eza.

## Files

- `template.yml` maps eza-native fields directly to Base2Tone coordinates.
- `tool.toml` describes the template and generated output path.

Color decisions belong in `template.yml`.

The shared compiler does not assign semantic meanings to Base2Tone coordinates.

## Manifest

    name = "eza"
    template = "template.yml"
    output = "eza/theme.yml"

## Output

The active generated theme is written to:

    generated/current/eza/theme.yml

## Validation

The generated theme must be tested by running eza with an isolated
`EZA_CONFIG_DIR`.

The validation environment should unset both `LS_COLORS` and `EZA_COLORS` so
those variables cannot hide errors in the generated native eza theme.
