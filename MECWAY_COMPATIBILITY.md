# Mecway / Native Beam Compatibility

The earlier development approach redirected ordinary `B31` input to the UB31 formulation. That approach has been retired to preserve CalculiX backward compatibility.

## Current approach

- `B31` remains the original CalculiX expanded beam element.
- `B31T` is the native-style 2-node Timoshenko interface backed by the UB31 kernel.
- `B31E` is the native-style 2-node Euler-Bernoulli interface backed by the UB31 kernel.
- Explicit `UB31` input remains available for user-element development.

Example:

```text
*ELEMENT, TYPE=B31T, ELSET=EBEAM
1, 1, 2

*BEAM SECTION, ELSET=EBEAM, MATERIAL=STEEL, SECTION=RECT
0.1, 0.2
0.0, 0.0, 1.0
```

This retains native-readable CalculiX-style input for preprocessors while avoiding any change in meaning for historical `B31` decks.

## Mecway

For a transparent Mecway workflow, the preferred long-term integration is for the exporter to emit `B31T` or `B31E` when the direct beam formulation is selected. If Mecway currently emits only `B31`, exporter support is required rather than overriding CalculiX's existing `B31` semantics.

See `NATIVE_BEAM_INTERFACE.md` and validation decks 16-18.

## Validation status

The parser and source changes are implemented on the development branch. Full rebuilt-executable regression is still required before the interface should be considered production-ready.
