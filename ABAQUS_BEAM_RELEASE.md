# Abaqus-compatible beam end releases for B31T/B31E

## Scope

This development branch adds the **Abaqus/Standard `*RELEASE`**
model-data keyword for native direct beams (`B31T`, `B31E`) and
explicit UB31 user beams. Existing `*USER BEAM RELEASE` syntax remains
available; legacy CalculiX `B31` is **not** converted or altered.

The parser routes `*RELEASE` to the existing element end-release
bitmask and static-condensation machinery, not to new stiffness code.

## Abaqus form

```inp
*ELEMENT, TYPE=B31T, ELSET=FRAME
1, 1, 2
2, 2, 3
*RELEASE
FRAME, S1, M1-M2
2, S2, ALLM
```

- Field 1: existing element number or ELSET name.
- Field 2: `S1` = first connectivity node, `S2` = second.
- Field 3: `M1`, `M2`, `T`, `M1-M2`, `M1-T`, `M2-T`, `ALLM`.
- Rotations: `M1` = local bending about beam local y (rotation DOF 5);
  `M2` = local bending about beam local z (rotation DOF 6);
  `T` = torsion about beam local x (rotation DOF 4).
- The `*RELEASE` parser accepts **only** the seven Abaqus combinations
  above and only `S1`/`S2`. It rejects numerical bitmasks and
  translational releases. `INPUT=` is not implemented.

Place the keyword after element/ELSET definitions and before `*STEP`.
Unreleased DOFs remain connected. Do not fully release every member
rotation connected to an otherwise unrestrained node: a free rotational
DOF can create a singular system. Support boundary conditions must
suppress any unused nodal rotations.

## Validation

Use `validation/20_native_b31t_abaqus_release.inp`.
A simply supported, 2 m long beam carries 1000 N at midspan.
Expected |Rz| at each end = 500 N and zero end bending moments for
the released bending axes. Midspan deflection can be compared with
`PL^3/(48EI)` plus the Timoshenko shear term `PL/(4 k G A)`.
The deck exercises both an ELSET target and an individual element ID.

**Status:** source implementation and test input only. A rebuilt CCX
binary and a successful runtime regression are required before relying
on the functionality in engineering production.

## Beam offsets are a separate feature

Existing UB31 code also supports *nonstandard* section-header parameters:
`OFFSET=(y,z)` for a uniform local y/z shift and
`OFFSET1=(x,y,z)` / `OFFSET2=(x,y,z)` for independent local nodal
eccentricities. These are interpreted by `src/userbeamsections.f` and
`src/e_c3d_ub31.f` (using rigid offset kinematic coupling).

They are **not** standard Abaqus `*BEAM SECTION OFFSET` syntax.
In Abaqus, `*BEAM SECTION OFFSET` is associated with
`*BEAM GENERAL SECTION` and specifies a cross-section origin shift.
It is not interchangeable with independently varying member-end
eccentricities. No change to offset syntax is included in this branch.
