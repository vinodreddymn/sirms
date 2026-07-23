"""
===============================================================================
SIRMS Deployment Toolkit

Module : database.py
Purpose: PostgreSQL Backup and Restore Operations
Version: 2.0
===============================================================================
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class DatabaseError(Exception):
    """Database operation failed."""


class DatabaseManager:
    """
    PostgreSQL Backup / Restore Manager
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        self.host = config["LOCAL_DB_HOST"]
        self.port = str(config["LOCAL_DB_PORT"])
        self.user = config["LOCAL_DB_USER"]
        self.password = config["LOCAL_DB_PASSWORD"]
        self.database = config["LOCAL_DB_NAME"]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _environment(self) -> dict:
        env = os.environ.copy()
        env["PGPASSWORD"] = self.password
        return env

    @staticmethod
    def _check_command(command: str):
        if shutil.which(command) is None:
            raise DatabaseError(f"{command} not found in PATH.")

    # ------------------------------------------------------------------
    # Backup
    # ------------------------------------------------------------------

    def backup(self, output_file: str | Path) -> Path:
        """
        Create PostgreSQL custom-format backup.
        """

        self._check_command("pg_dump")

        output = Path(output_file)

        cmd = [
            "pg_dump",
            "-h", self.host,
            "-p", self.port,
            "-U", self.user,
            "-F", "c",
            "-f", str(output),
            self.database,
        ]

        result = subprocess.run(
            cmd,
            env=self._environment(),
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise DatabaseError(result.stderr.strip())

        return output

    # ------------------------------------------------------------------
    # Restore
    # ------------------------------------------------------------------

    def restore(self, backup_file: str | Path):

        self._check_command("psql")
        self._check_command("pg_restore")

        backup = Path(backup_file)

        if not backup.exists():
            raise FileNotFoundError(backup)

        env = self._environment()

        subprocess.run(
            [
                "psql",
                "-h", self.host,
                "-p", self.port,
                "-U", self.user,
                "-d", "postgres",
                "-c",
                f"DROP DATABASE IF EXISTS {self.database};",
            ],
            env=env,
            check=True,
        )

        subprocess.run(
            [
                "psql",
                "-h", self.host,
                "-p", self.port,
                "-U", self.user,
                "-d", "postgres",
                "-c",
                f"CREATE DATABASE {self.database};",
            ],
            env=env,
            check=True,
        )

        subprocess.run(
            [
                "pg_restore",
                "-h", self.host,
                "-p", self.port,
                "-U", self.user,
                "-d", self.database,
                "--clean",
                "--if-exists",
                str(backup),
            ],
            env=env,
            check=True,
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate_backup(backup_file: str | Path) -> bool:

        backup = Path(backup_file)

        if not backup.exists():
            raise FileNotFoundError(backup)

        if backup.stat().st_size == 0:
            raise DatabaseError("Backup file is empty.")

        return True

    # ------------------------------------------------------------------
    # Information
    # ------------------------------------------------------------------

    @staticmethod
    def backup_info(backup_file: str | Path) -> dict:

        backup = Path(backup_file)

        stat = backup.stat()

        return {
            "filename": backup.name,
            "full_path": str(backup.resolve()),
            "size_bytes": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime),
            "modified": datetime.fromtimestamp(stat.st_mtime),
        }