"""Run Linked Structure Lab checks from the package directory.

Pre-commit executes hooks from the repository root. The package itself uses a
``src`` layout with tool configuration in its own ``pyproject.toml``, so this
small helper normalizes the working directory before delegating to each tool.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]

COMMANDS = {
    "ruff-check": [sys.executable, "-m", "ruff", "check", "."],
    "ruff-format": [sys.executable, "-m", "ruff", "format", "--check", "."],
    "mypy": [sys.executable, "-m", "mypy"],
    "pytest": [sys.executable, "-m", "pytest", "-q"],
}


def main() -> int:
    """Run the requested check and return its exit status."""
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        names = ", ".join(sorted(COMMANDS))
        print(f"Usage: run_check.py <{names}>", file=sys.stderr)
        return 2

    return subprocess.call(COMMANDS[sys.argv[1]], cwd=PACKAGE_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
