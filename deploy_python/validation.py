"""
===============================================================================
SIRMS Deployment Toolkit

Module : validation.py
Purpose : Environment Validation
Version : 2.0
===============================================================================
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from utils import command_exists


class ValidationError(Exception):
    """Raised when an environment validation fails."""


class ValidationManager:

    REQUIRED_PROJECT_DIRECTORIES = (
        "backend",
        "frontend",
        "database",
        "deploy",
    )

    REQUIRED_TOOLS = (
        "git",
        "ssh",
        "scp",
        "python",
        "node",
        "npm",
    )

    def __init__(self, config: dict):
        self.config = config

    # ------------------------------------------------------------------
    # Files & Directories
    # ------------------------------------------------------------------

    @staticmethod
    def required_directory(path: str | Path):

        path = Path(path)

        if not path.is_dir():
            raise ValidationError(
                f"Required directory not found: {path}"
            )

    @staticmethod
    def required_file(path: str | Path):

        path = Path(path)

        if not path.is_file():
            raise ValidationError(
                f"Required file not found: {path}"
            )

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    @staticmethod
    def required_command(command: str):

        if not command_exists(command):
            raise ValidationError(
                f"Required command not found: {command}"
            )

    # ------------------------------------------------------------------
    # Git Repository
    # ------------------------------------------------------------------

    def git_repository(self):

        project = Path(self.config["PROJECT_ROOT"])

        self.required_directory(project)
        self.required_directory(project / ".git")

    # ------------------------------------------------------------------
    # Project Structure
    # ------------------------------------------------------------------

    def project_structure(self):

        project = Path(self.config["PROJECT_ROOT"])

        for directory in self.REQUIRED_PROJECT_DIRECTORIES:

            self.required_directory(project / directory)

    # ------------------------------------------------------------------
    # SSH Key
    # ------------------------------------------------------------------

    def ssh_key(self):

        self.required_file(
            self.config["SSH_PRIVATE_KEY"]
        )

    # ------------------------------------------------------------------
    # PostgreSQL Client
    # ------------------------------------------------------------------

    def postgres_client(self):

        self.required_command("pg_dump")
        self.required_command("psql")

    # ------------------------------------------------------------------
    # Development Tools
    # ------------------------------------------------------------------

    def development_tools(self):

        for tool in self.REQUIRED_TOOLS:

            self.required_command(tool)

    # ------------------------------------------------------------------
    # PostgreSQL Connection
    # ------------------------------------------------------------------

    def database_connection(self):

        env = os.environ.copy()
        env["PGPASSWORD"] = self.config["LOCAL_DB_PASSWORD"]

        cmd = [
            "psql",
            "-h", self.config["LOCAL_DB_HOST"],
            "-p", str(self.config["LOCAL_DB_PORT"]),
            "-U", self.config["LOCAL_DB_USER"],
            "-d", self.config["LOCAL_DB_NAME"],
            "-c", "SELECT 1;",
        ]

        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise ValidationError(
                "Unable to connect to PostgreSQL.\n"
                + result.stderr.strip()
            )

    # ------------------------------------------------------------------
    # Complete Validation
    # ------------------------------------------------------------------

    def run(self) -> bool:

        self.development_tools()
        self.git_repository()
        self.project_structure()
        self.ssh_key()
        self.postgres_client()
        self.database_connection()

        return True