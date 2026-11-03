"""Build and install actual artifact bytes for isolated integration checks."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


def run_checked(args: list[str], cwd: Path, *, timeout: int = 180) -> str:
    """Run a checked command without repository path injection."""
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
    result = subprocess.run(
        args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


@dataclass(frozen=True)
class InstalledPackage:
    """Isolated installed interpreter and build inputs; no dev imports required."""

    python: Path
    workdir: Path
    artifact: Path

    def run(self, code: str) -> str:
        """Execute a program in isolated mode outside the repository."""
        return run_checked([str(self.python), "-I", "-c", code], self.workdir)
