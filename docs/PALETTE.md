# Base2Tone Palette

## Coordinate system

Each Base2Tone scheme contains four banks of eight coordinates:

    A0 A1 A2 A3 A4 A5 A6 A7
    B0 B1 B2 B3 B4 B5 B6 B7
    C0 C1 C2 C3 C4 C5 C6 C7
    D0 D1 D2 D3 D4 D5 D6 D7

The letter identifies a tonal family.

The number identifies a position within that family.

The coordinate itself is the stable identity. It is not a universal semantic
name.

## General dark-scheme observations

Across the upstream dark schemes, the following tendencies are common:

### A bank

The A bank usually provides:

- the darkest background values;
- raised or selected surfaces;
- borders and separators;
- quiet metadata;
- dim readable foreground values.

`A0` is normally the darkest structural anchor.

Higher A coordinates usually become progressively lighter, although the exact
lightness steps vary by scheme.

### B bank

The B bank is one chromatic family.

It often provides:

- secondary emphasis;
- navigation or path distinction;
- syntax or classification colors;
- brighter chromatic foregrounds.

Its hue, saturation, and starting lightness vary substantially between schemes.

### C bank

The C bank usually provides the most neutral or readable light ramp.

It often reaches the lightest values in a scheme.

Higher C coordinates are therefore useful candidates for:

- primary text;
- bright text;
- prominent headers;
- high-contrast foregrounds.

This remains a tendency rather than a fixed semantic rule.

### D bank

The D bank is the second chromatic family.

It often provides:

- stronger emphasis;
- current or active states;
- highlighted values;
- alternate syntax or classification colors.

It must not be assumed to mean success, warning, or accent globally.

## Numbered stops

A coordinate number is meaningful only within its own bank.

For example:

    A4
    B4
    C4
    D4

are not guaranteed to have identical lightness.

The number indicates a relative stop in that bank's authored ramp, not an
absolute cross-bank brightness level.

## Scheme variation

The existing schemes demonstrate several important variations:

- B and D may be close in hue.
- B and D may be complementary or nearly opposite.
- One bank may begin substantially lighter than another.
- Saturation may change unevenly through a ramp.
- Some ramps contain compressed or repeated lightness values.
- A middle coordinate may intentionally break a simple progression.

Examples such as Morning, Meadow, Space, Lavender, and Motel should be examined
when a template relies on a narrow contrast relationship.

## Mapping rule

A template should select coordinates according to:

1. the tool's native visual structure;
2. required foreground/background contrast;
3. hierarchy within the tool;
4. upstream Base2Tone application precedents;
5. consistency with related templates;
6. behavior across all schemes, not only one favorite scheme.

## Comments and exceptions

Common mappings do not require lengthy explanations on every line.

Comments are most useful when:

- a coordinate choice is not visually obvious;
- two nearby fields intentionally use different banks;
- a scheme irregularity affects the choice;
- a value is selected for contrast rather than category;
- the mapping intentionally differs from a related tool;
- the tool's schema forces an approximation.

## What this project will not do

This project will not define a global dictionary such as:

    BG = A0
    TEXT = C6
    SUCCESS = D4
    WARNING = D6
    DANGER = B2

Such a layer would hide the Base2Tone coordinates and assign universal meanings
that the palette does not guarantee.

Templates will instead use the coordinates directly and document their local
purpose.
