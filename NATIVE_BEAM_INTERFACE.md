# Native B31T / B31E Interface

This development branch keeps the historical CalculiX `B31` element unchanged and adds two native-style direct beam names backed by the UB31 kernel:

- `B31T` — 2-node 3D Timoshenko beam (shear deformation enabled using section shear factors).
- `B31E` — 2-node 3D Euler-Bernoulli beam (transverse shear deformation suppressed).
- `UB31` — the existing explicit user-element interface remains available for development and backward compatibility.

## Input syntax

```text
*ELEMENT, TYPE=B31T, ELSET=EBEAM
1, 1, 2

*MATERIAL, NAME=STEEL
*ELASTIC
2.1E11, 0.3

*BEAM SECTION, ELSET=EBEAM, MATERIAL=STEEL, SECTION=RECT
0.1, 0.2
0.0, 0.0, 1.0
```

Change `TYPE=B31T` to `TYPE=B31E` to select Euler-Bernoulli behavior. No `*USER ELEMENT` or `*USER BEAM SECTION` card is required for these two native-style names.

## Backward compatibility

`TYPE=B31` is deliberately **not** redirected. It remains the original CalculiX expanded beam element so existing input files retain their historical behavior.

Internally, the parser maps:

```text
B31T -> UB31T -> UB31 kernel (Timoshenko)
B31E -> UB31E -> UB31 kernel (Euler-Bernoulli)
```

The internal `T`/`E` marker is retained in `lakon(5:5)` and the UB31 kernel uses it to select the formulation. Plain `UB31` continues to use its existing section-card setting.

## Current scope

The native interface reuses the current UB31 section reader and therefore supports the section families already implemented there (`RECT`, `CIRC`, `PIPE`, `I`, `T`, `CHAN`, `L`, `BOX`). `SECTION=GENERAL` is not yet claimed as supported by this interface.

### CalculiX section-axis and dimension conventions

The direct beams now use the section-axis convention of CalculiX's
`*BEAM SECTION` definition:

- Longitudinal direction `t`: node 1 toward node 2.
- Local 1 direction: the global orientation vector on the line after
  the dimensions, projected perpendicular to `t`. If omitted, the
  CalculiX default vector `(0,0,-1)` is used. A deterministic alternative
  transverse direction is selected if this vector is parallel to the beam.
- Local 2 direction: `t x local1` (right-handed).
- `RECT`: first dimension along local 1, second along local 2.
  Accordingly `I11=a*b^3/12` and `I22=b*a^3/12` for
  `a=local1 thickness`, `b=local2 thickness`.
- `CIRC`: full elliptical diameters in local 1 and local 2, as in CCX;
  for a circle the two diameters are equal. The second defaults to the
  first if omitted. `PIPE` instead uses outer radius and wall thickness.
- `BOX`: dimensions `a,b,t1,t2,t3,t4`; `a` follows local 1 and `b`
  follows local 2. Wall thicknesses `t1,t2,t3,t4` correspond to the
  `+1,+2,-1,-2` faces. A zero wall remains a zero wall; the profile is
  **not** silently converted into `CHAN`.

The legacy `*USER BEAM SECTION, SECTION=CIRC` interface retains the
earlier radius input to avoid changing existing explicit `UB31` decks.
All other direct-beam section changes above also affect `UB31` when
those formulations share the property routine.

The automatic principal-axis transformation now uses the same positive
rotation about `t` as the local-frame transformation. For nonsymmetric
sections this is essential to avoid using inertia properties in a
different frame from the stiffness matrix.

### Mecway open-section compatibility

For example, an open BOX exported by Mecway can be represented by:

```text
*BEAM SECTION, ELSET=E1, MATERIAL=C180X70, SECTION=BOX
0.18,0.07,0.011,0.008,0.011,0
0,0,1
```

The file is interpreted in CalculiX BOX dimension/wall order, including
the zero fourth wall. The former implicit three-sided BOX -> CHAN
conversion is removed because it could transpose section dimensions
or lose which side was open. A different missing wall remains distinct.

The direct-beam implementation still requires full numerical
comparison against the original expanded CalculiX beam elements.
The thin-walled torsion and shear factors, in particular for open or
elliptical sections, are approximations and are **not** claims of
full equivalence with the expanded solid formulation. Explicit
`*NORMAL` per-node orientation is not yet implemented for these direct
beam elements.

If Mecway omits a section definition entirely, CCX has no geometric
dimensions to infer; an explicit `*BEAM SECTION` card is required.

### Regression checks

The standalone source regression can be built and run from the repository root:

```sh
gfortran -ffixed-line-length-none -c src/e_c3d_ubeam_utils.f -o /tmp/ubeam_utils.o
gfortran validation/test_ccx_beam_axes.f90 /tmp/ubeam_utils.o -o /tmp/ccx_beam_axes
/tmp/ccx_beam_axes
```

It checks unequal RECT sections, a full-diameter ellipse, a centred
closed BOX, mirrored open BOXes and the vanishing product of inertia
after L-section principal-axis rotation.

The implementation has source-level checks but still requires full rebuilt-CCX runtime regression before being considered production-ready.