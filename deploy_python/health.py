"""
===============================================================================
SIRMS Deployment Toolkit

Module : health.py
Purpose : Health Check Operations
Version : 2.0
===============================================================================
"""

from __future__ import annotations

import shutil
import socket
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class HttpHealthResult:
    url: str
    success: bool
    status_code: int | None = None
    error: str | None = None


@dataclass
class DiskHealthResult:
    path: str
    free_gb: float
    total_gb: float
    used_gb: float
    percent_used: float


@dataclass
class HealthReport:
    backend: HttpHealthResult
    frontend: HttpHealthResult
    backend_port: bool
    disk: DiskHealthResult
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend": asdict(self.backend),
            "frontend": asdict(self.frontend),
            "backend_port": self.backend_port,
            "disk": asdict(self.disk),
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# Health Manager
# =============================================================================

class HealthManager:

    def __init__(self, config: dict):
        self.config = config

    # -------------------------------------------------------------------------
    # HTTP Endpoint
    # -------------------------------------------------------------------------

    @staticmethod
    def test_http_endpoint(
        url: str,
        timeout: int = 15,
    ) -> HttpHealthResult:

        try:
            response = requests.get(url, timeout=timeout)

            return HttpHealthResult(
                url=url,
                success=200 <= response.status_code < 300,
                status_code=response.status_code,
            )

        except Exception as ex:
            return HttpHealthResult(
                url=url,
                success=False,
                error=str(ex),
            )

    # -------------------------------------------------------------------------
    # TCP Port
    # -------------------------------------------------------------------------

    @staticmethod
    def test_tcp_port(
        host: str,
        port: int,
        timeout: int = 3,
    ) -> bool:

        try:
            with socket.create_connection(
                (host, port),
                timeout=timeout,
            ):
                return True

        except Exception:
            return False

    # -------------------------------------------------------------------------
    # Disk Space
    # -------------------------------------------------------------------------

    @staticmethod
    def test_disk_space(
        path: str | Path = ".",
    ) -> DiskHealthResult:

        usage = shutil.disk_usage(path)

        total = usage.total / (1024 ** 3)
        free = usage.free / (1024 ** 3)
        used = usage.used / (1024 ** 3)

        percent = (used / total) * 100

        return DiskHealthResult(
            path=str(Path(path).resolve()),
            free_gb=round(free, 2),
            total_gb=round(total, 2),
            used_gb=round(used, 2),
            percent_used=round(percent, 2),
        )

    # -------------------------------------------------------------------------
    # Complete Health Check
    # -------------------------------------------------------------------------

    def run(self) -> HealthReport:

        return HealthReport(
            backend=self.test_http_endpoint(
                self.config["BACKEND_HEALTH_URL"]
            ),
            frontend=self.test_http_endpoint(
                self.config["FRONTEND_HEALTH_URL"]
            ),
            backend_port=self.test_tcp_port(
                "127.0.0.1",
                5000,
            ),
            disk=self.test_disk_space(),
            timestamp=datetime.now(),
        )