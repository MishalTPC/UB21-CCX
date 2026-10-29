"""Check that Mecway opt-in changes the expected bending displacement."""
import math
import re
import sys

FLOAT = re.compile(r"[+-]?\d+\.\d+E[+-]\d+", re.IGNORECASE)

def midspan_uz(path):
    in_disp = False
    for line in open(path, encoding="utf-8", errors="replace"):
        if line.startswith(" -4  DISP"):
            in_disp = True
            continue
        if in_disp and line.startswith(" -3"):
            in_disp = False
        if in_disp and line.startswith(" -1"):
            match = re.match(r"\s*(\d+)(.*)", line[3:])
            if match and int(match.group(1)) == 2:
                values = [float(x) for x in FLOAT.findall(match.group(2))]
                if len(values) >= 3:
                    return values[2]
    raise RuntimeError(f"No node 2 DISP field found in {path}")

normal, compat = [midspan_uz(path) for path in sys.argv[1:3]]
print(f"Normal Uz(node 2)={normal:.10e} m")
print(f"Mecway mode Uz(node 2)={compat:.10e} m")
if not all(math.isfinite(x) for x in (normal, compat)):
    raise SystemExit("ERROR: invalid displacement")
if math.isclose(normal, compat, rel_tol=1e-5, abs_tol=1e-13):
    raise SystemExit("ERROR: Mecway release compatibility did not change Uz")
