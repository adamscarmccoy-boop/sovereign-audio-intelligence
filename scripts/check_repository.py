"""Read-only checks of committed public documentation and data-file structure.

This is NOT an audio performance benchmark or a test of the local workstation.
It uses only Python's standard library and exits non-zero on failure.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = (
    "README.md",
    "docs/SOVEREIGN_MUSIC_ENGINE_ARCHITECTURE_2026-11-12.md",
    "docs/OPERATIONS_AND_SCHEDULES.md",
    "Sovereign_Audio_Intelligence_Engine.ipynb",
    "audio_deep_dive_report.parquet",
    ".github/workflows/perf-audit.yml",
)

LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def check() -> list[str]:
    errors: list[str] = []
    for item in REQUIRED:
        p = ROOT / item
        if not p.is_file() or p.stat().st_size == 0:
            errors.append(f"Missing or empty committed file: {item}")

    for item in ("README.md", "docs/SOVEREIGN_MUSIC_ENGINE_ARCHITECTURE_2026-11-12.md", "docs/OPERATIONS_AND_SCHEDULES.md"):
        p = ROOT / item
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        if text.count("```") % 2:
            errors.append(f"Unclosed code fence in {item}")
        for match in LINK.finditer(text):
            target = match.group(1).split("#", 1)[0].split("?", 1)[0].strip()
            if not target or target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            if target.startswith(("/", "\\")):
                errors.append(f"Unsafe absolute local link in {item}: {target}")
                continue
            resolved = (p.parent / target).resolve()
            if not resolved.is_relative_to(ROOT.resolve()) or not resolved.exists():
                errors.append(f"Broken local link in {item}: {target}")

    notebook = ROOT / "Sovereign_Audio_Intelligence_Engine.ipynb"
    if notebook.exists():
        try:
            obj = json.loads(notebook.read_text(encoding="utf-8"))
            if not isinstance(obj.get("cells"), list):
                errors.append("Notebook does not contain a cells array")
        except (OSError, ValueError) as exc:
            errors.append(f"Notebook JSON invalid: {exc}")

    parquet = ROOT / "audio_deep_dive_report.parquet"
    if parquet.exists():
        with parquet.open("rb") as handle:
            first = handle.read(4)
            handle.seek(-4, 2)
            last = handle.read(4)
        if first != b"PAR1" or last != b"PAR1":
            errors.append("Sample Parquet header/footer is invalid")

    return errors


def main() -> int:
    problems = check()
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        return 1
    print("PASS: public document links, required files, notebook JSON and Parquet file signature")
    print("NOTE: no audio inference, native kernel, latency or workstation test was performed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
