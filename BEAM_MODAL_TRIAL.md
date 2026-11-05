# Beam formulation and modal trial (experimental)

Separate branch `fix/beam-section-modal-validation-20261105` from
`dev` commit `e7907310ba8272bc4efb9a463bb9d26a19f63001`.

Fixes:
- The principal bending axes of asymmetric sections now use the
  same physical rotation and inertia transformation, including
  signed bending coupling in angle sections.
- B31E member-force recovery now uses Euler-Bernoulli stiffness,
  while B31T uses automatic Timoshenko shear factors and UB31
  honours its KAPPA/TIMOSHENKO option.
- Windows build adds an independent 70x70x8 mm angle coupling test
  and B31E/B31T modal solver smoke tests. The default `dev`
  branch remains unchanged.

The mass matrix is *unchanged*: the existing approach uses a two-node
consistent bending mass matrix plus rotary section inertia. Different
natural frequencies between B31T and Mecway/Code_Aster Euler-Bernoulli
beams can reflect differences in stiffness formulation, cross-section
properties or mass/inertia assumptions. No numerical modal correlation
to Mecway or Code_Aster is claimed.

Download the branch-specific artifact from GitHub Actions after the
Windows workflow succeeds:
`ccx-2.23-beam-validation-windows-x86_64`.

Run `validation/23_b31e_modal_cantilever.inp` and
`validation/24_b31t_modal_cantilever.inp` to separate formulation
effects, then compare extracted frequencies on your full model.

Existing optional `CCX_MECWAY_SWAP_RELEASE_AXES=1` remains available
for the Mecway *RELEASE mapping workaround.

WARNING: experimental engineering solver. Nonlinear response,
eccentric offsets/end-release combinations, noncircular torsional
stresses, open-section shear coefficients, and production modal accuracy
are not comprehensively validated in this branch.

## Open-section Saint-Venant torsion update

The open-section I/T/channel/angle torsion constant now comes from a
numerical solution of the Prandtl stress-function equation on the
cross-section, using a uniform finite-difference grid and conjugate
gradients. Repeated section dimensions are cached. The previous
thin-wall plate-sum formula remains an automatic fallback for
unsupported or oversized grids.

Set `CCX_LEGACY_OPEN_TORSION=1` in the environment to recover the
previous torsion constants for A/B comparisons in the same executable.
This does not change `A`, `Iyy`, `Izz`, or material properties.

For the supplied approximate dimensions, numerically computed J:
- C180x70 (h=180mm,b=70mm,tf=11mm,tw=8mm):
  8.50335e-8 m^4 (previous 8.74067e-8)
- L70x70x8: 2.19566e-8 m^4 (previous 2.2528e-8).

Independent frame model indicates this reduces the original
approximately 3.4% displacement discrepancy to approximately 1.26%.
The residual is **not** yet explained. This is an experimental solver
correction, not a claim of full Mecway parity or production readiness.

The idealized section model does not capture fillet radii, cold-formed
corner rounding, welds, or warping effects. For full accuracy, section
properties and eccentricities should ultimately be matched with the
reference solver.
