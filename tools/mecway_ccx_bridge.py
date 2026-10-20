#!/usr/bin/env python3
"""
Mecway -> enhanced CalculiX bridge (prototype)

V1 capabilities:
- Patch CalculiX beam element cards to B31T or B31E.
- Insert *USER BEAM RELEASE cards from a JSON sidecar.
- Run the enhanced ccx_2.23 executable.
- Preserve standard CalculiX output names so Mecway can read .frd/.dat/.sta.

This version does NOT yet read Mecway .liml flexible-joint objects automatically.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def load_config(path: Path | None) -> dict:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def patch_element_types(text: str, beam_type: str | None) -> str:
    if not beam_type:
        return text

    beam_type = beam_type.upper()
    if beam_type not in {"B31T", "B31E"}:
        raise ValueError("beam_type must be B31T or B31E")

    # Only replace plain B31 element cards. Existing B31T/B31E remain unchanged.
    pattern = re.compile(
        r"(^\s*\*ELEMENT\s*,[^\n]*\bTYPE\s*=\s*)B31(?=\s*(?:,|$))",
        re.IGNORECASE | re.MULTILINE,
    )
    return pattern.sub(rf"\1{beam_type}", text)


def make_release_block(releases: list[dict]) -> str:
    if not releases:
        return ""

    lines = [
        "** Added by mecway_ccx_bridge.py",
        "*USER BEAM RELEASE",
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
            lines.append(f"{target},{end},{code}")
        else:
            lines.append(f"{target},{end},{code},{spring}")

    return "\n".join(lines) + "\n"


def insert_before_first_step(text: str, block: str) -> str:
    if not block:
        return text

    match = re.search(r"^\s*\*STEP\b", text, re.IGNORECASE | re.MULTILINE)
    if not match:
        raise ValueError("No *STEP keyword found in input deck")

    return text[: match.start()] + block + text[match.start() :]


def run_ccx(ccx: Path, inp: Path) -> int:
    # CalculiX expects the job name without .inp.
    job = inp.stem
    cwd = inp.parent
    command = [str(ccx.resolve()), job]

    print("Running:", " ".join(command))
    completed = subprocess.run(command, cwd=cwd)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Patch a Mecway CalculiX deck and run enhanced CCX."
    )
    parser.add_argument("inp", type=Path, help="Mecway-generated .inp file")
    parser.add_argument(
        "--ccx",
        type=Path,
        required=True,
        help="Path to enhanced ccx_2.23.exe / ccx_2.23",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Optional JSON file containing beam_type and releases",
    )
    parser.add_argument(
        "--beam-type",
        choices=["B31T", "B31E"],
        help="Override plain B31 element cards globally",
    )
    parser.add_argument(
        "--no-run",
        action="store_true",
        help="Patch the deck but do not launch CCX",
    )
    args = parser.parse_args()

    inp = args.inp.resolve()
    if not inp.exists():
        print(f"Input file not found: {inp}", file=sys.stderr)
        return 2

    config = load_config(args.config)
    beam_type = args.beam_type or config.get("beam_type")
    releases = config.get("releases", [])

    original = inp.read_text(encoding="utf-8", errors="replace")
    patched = patch_element_types(original, beam_type)
    patched = insert_before_first_step(patched, make_release_block(releases))

    backup = inp.with_suffix(inp.suffix + ".mecway-original")
    if not backup.exists():
        shutil.copy2(inp, backup)

    inp.write_text(patched, encoding="utf-8", newline="\n")

    print(f"Patched input: {inp}")
    print(f"Original backup: {backup}")
    if beam_type:
        print(f"Beam type: {beam_type}")
    print(f"Beam releases added: {len(releases)}")

    if args.no_run:
        return 0

    if not args.ccx.exists():
        print(f"CCX executable not found: {args.ccx}", file=sys.stderr)
        return 2

    rc = run_ccx(args.ccx, inp)

    expected = {
        ".frd": inp.with_suffix(".frd"),
        ".dat": inp.with_suffix(".dat"),
        ".sta": inp.with_suffix(".sta"),
    }
    for ext, path in expected.items():
        print(f"{ext}: {'OK' if path.exists() else 'not produced'} - {path}")

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
