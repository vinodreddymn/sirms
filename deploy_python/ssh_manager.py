"""
===============================================================================
SIRMS Deployment Toolkit

Module : ssh_manager.py
Purpose : SSH Operations
Version : 2.0
===============================================================================
"""

from __future__ import annotations

import shutil
from pathlib import Path

import paramiko


class SSHError(Exception):
    """Raised when an SSH operation fails."""


class SSHManager:

    def __init__(
        self,
        host: str,
        user: str,
        key_file: str | Path,
        port: int = 22,
        timeout: int = 30,
    ):

        self.host = host
        self.user = user
        self.port = port
        self.timeout = timeout
        self.key_file = Path(key_file)

        if not self.key_file.exists():
            raise FileNotFoundError(self.key_file)

        self.client: paramiko.SSHClient | None = None

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def connect(self):

        if self.client:
            return

        self.client = paramiko.SSHClient()

        self.client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )

        self.client.connect(
            hostname=self.host,
            username=self.user,
            port=self.port,
            key_filename=str(self.key_file),
            timeout=self.timeout,
        )

    def close(self):

        if self.client:
            self.client.close()
            self.client = None

    # ------------------------------------------------------------------
    # Context Manager
    # ------------------------------------------------------------------

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # ------------------------------------------------------------------
    # Command Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        command: str,
        check: bool = True,
    ) -> str:

        self.connect()

        stdin, stdout, stderr = self.client.exec_command(command)

        exit_code = stdout.channel.recv_exit_status()

        out = stdout.read().decode().strip()

        err = stderr.read().decode().strip()

        if check and exit_code != 0:
            raise SSHError(
                f"Command failed ({exit_code})\n{err}"
            )

        return out

    # ------------------------------------------------------------------
    # Directory
    # ------------------------------------------------------------------

    def ensure_directory(
        self,
        directory: str,
    ):

        self.execute(
            f"mkdir -p '{directory}'"
        )

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    def upload(
        self,
        local_file: str | Path,
        remote_directory: str,
    ):

        local = Path(local_file)

        if not local.exists():
            raise FileNotFoundError(local)

        self.ensure_directory(remote_directory)

        remote_file = (
            remote_directory.rstrip("/")
            + "/"
            + local.name
        )

        self.connect()

        with self.client.open_sftp() as sftp:
            sftp.put(
                str(local),
                remote_file,
            )

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    def download(
        self,
        remote_file: str,
        local_directory: str | Path,
    ):

        local_dir = Path(local_directory)

        local_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        local_file = local_dir / Path(remote_file).name

        self.connect()

        with self.client.open_sftp() as sftp:
            sftp.get(
                remote_file,
                str(local_file),
            )

        return local_file

    # ------------------------------------------------------------------
    # Upload Directory
    # ------------------------------------------------------------------

    def upload_directory(
        self,
        local_directory: str | Path,
        remote_directory: str,
    ):

        local_directory = Path(local_directory)

        if not local_directory.exists():
            raise FileNotFoundError(local_directory)

        for file in local_directory.rglob("*"):

            if file.is_dir():
                continue

            relative = file.relative_to(local_directory)

            remote_dir = (
                remote_directory.rstrip("/")
                + "/"
                + str(relative.parent).replace("\\", "/")
            )

            self.ensure_directory(remote_dir)

            with self.client.open_sftp() as sftp:

                sftp.put(
                    str(file),
                    remote_dir.rstrip("/")
                    + "/"
                    + file.name,
                )

    # ------------------------------------------------------------------
    # Test
    # ------------------------------------------------------------------

    def test_connection(self) -> bool:

        try:

            self.execute(
                "echo connected"
            )

            return True

        except Exception:

            return False