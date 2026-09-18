# Mecway B31 compatibility

This fork routes conventional CalculiX `B31` input to the native two-node
`UB31` formulation so that a Mecway-exported beam deck does not need an
external text-conversion step.

## Accepted input

```text
*ELEMENT, TYPE=B31, ELSET=EBEAM
1, 1, 2

*BEAM SECTION, ELSET=EBEAM, MATERIAL=STEEL, SECTION=RECT
0.1, 0.2
0.0, 0.0, 1.0
```

For these `B31` elements the input reader internally stores `UB31` and uses
the UB31 kernel. `*BEAM SECTION` is routed to the existing UB31 section
property reader when its target element set contains these elements.

The original explicit syntax remains available:

```text
*USER ELEMENT, TYPE=UB31, NODES=2, MAXDOF=6, INTEGRATIONPOINTS=1
*ELEMENT, TYPE=UB31, ELSET=EBEAM
...
*USER BEAM SECTION, ELSET=EBEAM, MATERIAL=STEEL, SECTION=RECT
...
```

## Scope of this first compatibility patch

- `B31` is routed to `UB31` with 2 nodes, 6 DOF/node and 1 integration point.
- Standard `*BEAM SECTION` is routed to `userbeamsections()` for UB31 sets.
- Existing non-UB31 beam section handling is retained.
- Existing explicit UB31 input remains supported.

Regression input: `validation/mecway_b31_alias.inp`.
