# Glow

This module owns the complete Base2Tone style for Glow and its Glamour
Markdown renderer.

## Files

- `template.json` maps Glow and Chroma fields directly to Base2Tone
  coordinates.
- `tool.toml` declares the native JSON template, output, and validator.
- `validate.py` checks structure, colors, Chroma coverage, and rendering through
  Glow.

## Manifest

    name = "glow"
    template = "template.json"
    output = "glow/style.json"
    validator = "validate.py"

## Output

    generated/current/glow/style.json

## Mapping approach

Ordinary prose, operators, punctuation, and supporting structure remain
restrained. Stronger coordinates identify headings, links, keywords, names,
and other content that benefits from fast visual recognition.

The template uses only direct Base2Tone coordinates and introduces no second
semantic palette.

## Validation

Validation checks JSON syntax, expected Glow sections, the maintained Chroma
field set, hexadecimal colors, unresolved coordinates, and an isolated
Markdown render through Glow.
