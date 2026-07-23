"""
===============================================================================
SIRMS Deployment Toolkit

Module : utils.py
Purpose : Common Utility Functions
Version : 2.0
===============================================================================
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class ProcessResult:
    exit_code: int
    stdout: str
    stderr: str
    success: bool


# =============================================================================
# Utility Functions
# =============================================================================

def get_timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """
    Return the current timestamp.
    """
    return datetime.now().strftime(fmt)


# -----------------------------------------------------------------------------


def ensure_directory(path: str | Path) -> Path:
    """
    Create a directory if it doesn't exist.
    """
    directory = Path(path).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    return directory


# -----------------------------------------------------------------------------


def command_exists(command: str) -> bool:
    """
    Check whether an executable exists in PATH.
    """
    return shutil.which(command) is not None


# -----------------------------------------------------------------------------


def run_process(
    executable: str,
    arguments: list[str] | None = None,
    working_directory: str | Path | None = None,
    ignore_exit_code: bool = False,
) -> ProcessResult:
    """
    Execute an external process.
    """

    arguments = arguments or []

    result = subprocess.run(
        [executable, *arguments],
        cwd=working_directory,
        capture_output=True,
        text=True,
    )

    if not ignore_exit_code and result.returncode != 0:
        raise RuntimeError(
            f"{executable} failed.\n\n"
            f"{result.stderr.strip()}"
        )

    return ProcessResult(
        exit_code=result.returncode,
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
        success=result.returncode == 0,
    )


# -----------------------------------------------------------------------------


def get_elapsed_time(
    start: datetime,
    end: datetime,
) -> str:
    """
    Return elapsed time as HH:MM:SS.
    """

    seconds = int((end - start).total_seconds())

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"


# -----------------------------------------------------------------------------


def get_file_checksum(
    path: str | Path,
) -> str:
    """
    Calculate SHA-256 checksum.
    """

    file = Path(path)

    sha = hashlib.sha256()

    with file.open("rb") as fp:

        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            sha.update(chunk)

    return sha.hexdigest()


# -----------------------------------------------------------------------------


def remove_old_files(
    directory: str | Path,
    keep: int,
    pattern: str = "*",
):
    """
    Keep only the newest N files.
    """

    directory = Path(directory)

    if not directory.exists():
        return

    files = sorted(
        directory.glob(pattern),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    for file in files[keep:]:

        if file.is_file():
            file.unlink()


# -----------------------------------------------------------------------------


def is_administrator() -> bool:
    """
    Returns True if running with Administrator/root privileges.
    """

    if os.name == "nt":

        import ctypes

        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    return os.geteuid() == 0


# -----------------------------------------------------------------------------


def resolve_path(
    path: str | Path,
) -> Path:
    """
    Return an absolute Path object.
    """

    return Path(path).expanduser().resolve()