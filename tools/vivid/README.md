# vivid

This module owns the Base2Tone integration for vivid and LS_COLORS.

## Files

- `template.yml` maps vivid-native categories directly to Base2Tone
  coordinates.
- `tool.toml` declares the rendered theme and local post-processing hook.
- `build.py` runs vivid against the rendered theme and creates a reusable Zsh
  fragment exporting LS_COLORS.

## Manifest

    name = "vivid"
    template = "template.yml"
    output = "vivid/theme.yml"
    postprocess = "build.py"

## Outputs

    generated/current/vivid/theme.yml
    generated/current/vivid/ls-colors.zsh

## Coordinate names

The template's local vivid color table uses names such as `A4`, `B5`, and `D4`.

These are the original Base2Tone coordinates, not semantic aliases.

## Validation

A successful build requires:

1. vivid to parse the rendered YAML theme;
2. `vivid generate` to return a non-empty LS_COLORS expression;
3. the generated Zsh fragment to be valid when sourced.
