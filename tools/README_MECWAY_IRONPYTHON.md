# Mecway IronPython Bridge

This version is intended for Mecway's embedded Microsoft.Scripting / IronPython environment.

It avoids Python 3-only features such as:
- from __future__ import annotations
- pathlib
- function type hints
- f-strings

## Setup

Open `mecway_ccx_bridge_ironpython.py` and change:

```python
CCX_EXE = r"C:\CCX\ccx_2.23.exe"
```

to the actual location of your enhanced CCX build.

For an initial manual test, also set:

```python
INP_FILE = r"C:\path\to\your\mecway_generated.inp"
```

The script patches the deck and launches the specified CCX executable.

The next integration step is to obtain Mecway's generated working-directory/input filename automatically so that `INP_FILE` does not need to be entered manually.
