# Mecway -> Enhanced CalculiX Bridge

This is an initial Python wrapper for using the enhanced B31T/B31E CalculiX build with Mecway.

## What V1 does

1. Reads a Mecway-generated CalculiX `.inp` file.
2. Optionally changes plain `TYPE=B31` cards to `B31T` or `B31E`.
3. Inserts `*USER BEAM RELEASE` definitions before the first `*STEP`.
4. Runs the enhanced CalculiX executable.
5. Leaves the normal CalculiX result files (`.frd`, `.dat`, `.sta`) beside the job so Mecway can use its ordinary result-import path.

V1 deliberately does **not** recreate Mecway's exporter. Mecway remains responsible for nodes, elements, materials, loads, restraints, steps, and normal output requests.

V1 also does **not yet** read Mecway `.liml` flexible-joint/release objects automatically. A JSON sidecar is used for release definitions until the Mecway model representation is mapped.

## Example

Windows:

```text
python tools\mecway_ccx_bridge.py model.inp ^
  --ccx C:\CCX\ccx_2.23.exe ^
  --config tools\mecway_bridge_example.json
```

Patch only, without launching CCX:

```text
python tools\mecway_ccx_bridge.py model.inp ^
  --ccx C:\CCX\ccx_2.23.exe ^
  --config tools\mecway_bridge_example.json ^
  --no-run
```

## Release configuration

```json
{
  "beam_type": "B31T",
  "releases": [
    {
      "target": "E1",
      "end": 1,
      "code": "M1-M2"
    }
  ]
}
```

`target` may be an element number or an element-set name accepted by the enhanced `*USER BEAM RELEASE` parser.

## Next development step

Read Mecway flexible-joint/end-release definitions directly from the `.liml` model and map geometric member ends to the terminal CalculiX element/end automatically. That removes the JSON release list and makes the bridge suitable for a one-click Mecway workflow.
