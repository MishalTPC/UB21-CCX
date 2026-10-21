# Mecway -> Enhanced CalculiX bridge
# IronPython/Microsoft.Scripting compatible version
#
# Edit the three settings below when running directly from Mecway.
# You may also call this script from a normal command line with arguments.

import os
import re
import json
import shutil
import subprocess
import sys

# ----------------------------------------------------------------------
# MECWAY SETTINGS
# ----------------------------------------------------------------------
# Point this to YOUR enhanced CCX build:
CCX_EXE = r"C:\CCX\ccx_2.23.exe"

# If Mecway gives the script a generated .inp path through argv, that path
# is used automatically. Otherwise put a test .inp path here.
INP_FILE = r""

# Optional release configuration JSON. Leave blank for no release sidecar.
CONFIG_FILE = r""

# Default formulation used when plain TYPE=B31 appears in the generated deck.
DEFAULT_BEAM_TYPE = "B31T"

# Set True if you only want to patch the deck without launching CCX.
PATCH_ONLY = False
# ----------------------------------------------------------------------


def load_config(path):
    if not path:
        return {}
    f = open(path, "r")
    try:
        return json.load(f)
    finally:
        f.close()


def read_text(path):
    f = open(path, "r")
    try:
        return f.read()
    finally:
        f.close()


def write_text(path, text):
    f = open(path, "w")
    try:
        f.write(text)
    finally:
        f.close()


def patch_element_types(text, beam_type):
    if not beam_type:
        return text

    beam_type = beam_type.upper()
    if beam_type not in ("B31T", "B31E"):
        raise ValueError("beam_type must be B31T or B31E")

    pattern = re.compile(
        r"(^\s*\*ELEMENT\s*,[^\n]*\bTYPE\s*=\s*)B31(?=\s*(?:,|$))",
        re.IGNORECASE | re.MULTILINE
    )

    def repl(match):
        return match.group(1) + beam_type

    return pattern.sub(repl, text)


def make_release_block(releases):
    if not releases:
        return ""

    lines = [
        "** Added by mecway_ccx_bridge_ironpython.py",
        "*USER BEAM RELEASE"
    ]

    for item in releases:
        target = item.get("target")
        end = item.get("end")
        code = item.get("code")
        spring = item.get("spring")

        if target is None or end not in (1, 2) or not code:
            raise ValueError(
                "Each release requires target, end (1 or 2), and code"
            )

        if spring is None:
            lines.append("%s,%s,%s" % (target, end, code))
        else:
            lines.append("%s,%s,%s,%s" % (target, end, code, spring))

    return "\n".join(lines) + "\n"


def insert_before_first_step(text, block):
    if not block:
        return text

    match = re.search(r"^\s*\*STEP\b", text, re.IGNORECASE | re.MULTILINE)
    if not match:
        raise ValueError("No *STEP keyword found in input deck")

    return text[:match.start()] + block + text[match.start():]


def run_ccx(ccx_exe, inp_path):
    inp_path = os.path.abspath(inp_path)
    ccx_exe = os.path.abspath(ccx_exe)
    workdir = os.path.dirname(inp_path)
    job = os.path.splitext(os.path.basename(inp_path))[0]

    print("Running CCX:")
    print("  executable: " + ccx_exe)
    print("  job:        " + job)
    print("  directory:  " + workdir)

    p = subprocess.Popen([ccx_exe, job], cwd=workdir)
    return p.wait()


def resolve_paths():
    inp_path = INP_FILE
    cfg_path = CONFIG_FILE
    ccx_path = CCX_EXE
    beam_type = DEFAULT_BEAM_TYPE
    patch_only = PATCH_ONLY

    # Optional command-line support:
    # script.py model.inp [ccx.exe] [config.json] [B31T|B31E]
    if len(sys.argv) > 1 and sys.argv[1]:
        inp_path = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2]:
        ccx_path = sys.argv[2]
    if len(sys.argv) > 3 and sys.argv[3]:
        cfg_path = sys.argv[3]
    if len(sys.argv) > 4 and sys.argv[4]:
        beam_type = sys.argv[4]

    return inp_path, ccx_path, cfg_path, beam_type, patch_only


def main():
    inp_path, ccx_path, cfg_path, beam_type, patch_only = resolve_paths()

    if not inp_path:
        raise Exception(
            "No .inp file specified. Set INP_FILE near the top of the script "
            "or pass the generated .inp file as the first argument."
        )

    inp_path = os.path.abspath(inp_path)

    if not os.path.isfile(inp_path):
        raise Exception("Input file not found: " + inp_path)

    config = load_config(cfg_path)
    if config.get("beam_type"):
        beam_type = config.get("beam_type")

    releases = config.get("releases", [])

    original = read_text(inp_path)
    patched = patch_element_types(original, beam_type)
    patched = insert_before_first_step(
        patched,
        make_release_block(releases)
    )

    backup = inp_path + ".mecway-original"
    if not os.path.exists(backup):
        shutil.copy2(inp_path, backup)

    write_text(inp_path, patched)

    print("Patched input: " + inp_path)
    print("Original backup: " + backup)
    print("Beam type: " + str(beam_type))
    print("Beam releases added: " + str(len(releases)))

    if patch_only:
        print("PATCH_ONLY=True: CCX was not started.")
        return 0

    if not os.path.isfile(ccx_path):
        raise Exception("CCX executable not found: " + ccx_path)

    rc = run_ccx(ccx_path, inp_path)

    base = os.path.splitext(inp_path)[0]
    for ext in (".frd", ".dat", ".sta"):
        p = base + ext
        if os.path.exists(p):
            print(ext + ": OK - " + p)
        else:
            print(ext + ": not produced - " + p)

    return rc


try:
    _rc = main()
    print("Bridge finished with return code: " + str(_rc))
except Exception as exc:
    print("Mecway CCX bridge error:")
    print(str(exc))
    raise
