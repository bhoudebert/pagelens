from __future__ import annotations

import subprocess
import sys

COMMANDS = [
    ["ruff", "format", "--check", "."],
    ["ruff", "check", "."],
    ["mypy"],
    ["pytest", "--cov=pagelens", "--cov-report=term-missing"],
]


def main() -> int:
    for command in COMMANDS:
        result = subprocess.run(command, check=False)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
