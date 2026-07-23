"""
===============================================================================
SIRMS Deployment Toolkit

Module : report.py
Purpose : Deployment Report Generation
Version : 2.0
===============================================================================
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any


class ReportManager:

    def __init__(self, report_directory: str | Path):

        self.report_directory = Path(report_directory)
        self.report_directory.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Internal
    # -------------------------------------------------------------------------

    @staticmethod
    def _serialise(value: Any):

        if is_dataclass(value):
            return asdict(value)

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, Path):
            return str(value)

        return value

    # -------------------------------------------------------------------------
    # JSON Report
    # -------------------------------------------------------------------------

    def _write_json(
        self,
        context: dict,
        filename: Path,
    ):

        serialised = {
            key: self._serialise(value)
            for key, value in context.items()
        }

        filename.write_text(
            json.dumps(
                serialised,
                indent=4,
                default=str,
            ),
            encoding="utf-8",
        )

    # -------------------------------------------------------------------------
    # HTML Report
    # -------------------------------------------------------------------------

    def _write_html(
        self,
        context: dict,
        filename: Path,
    ):

        rows = []

        for key, value in context.items():

            if isinstance(value, (dict, list)):
                value = json.dumps(value, indent=2)

            rows.append(
                f"""
<tr>
<td>{escape(str(key))}</td>
<td><pre>{escape(str(value))}</pre></td>
</tr>
"""
            )

        html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="utf-8">

<title>SIRMS Deployment Report</title>

<style>

body {{
    font-family: Segoe UI, Arial;
    margin: 30px;
}}

table {{
    width:100%;
    border-collapse:collapse;
}}

th, td {{
    border:1px solid #cccccc;
    padding:8px;
    vertical-align:top;
}}

th {{
    background:#f2f2f2;
}}

pre {{
    margin:0;
    white-space:pre-wrap;
}}

</style>

</head>

<body>

<h2>SIRMS Deployment Report</h2>

<table>

<tr>
<th>Property</th>
<th>Value</th>
</tr>

{''.join(rows)}

</table>

</body>

</html>
"""

        filename.write_text(
            html,
            encoding="utf-8",
        )

    # -------------------------------------------------------------------------
    # Public
    # -------------------------------------------------------------------------

    def create(
        self,
        context: dict,
    ) -> dict:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        json_file = (
            self.report_directory
            / f"deployment_{timestamp}.json"
        )

        html_file = (
            self.report_directory
            / f"deployment_{timestamp}.html"
        )

        self._write_json(context, json_file)

        self._write_html(context, html_file)

        return {
            "json": json_file,
            "html": html_file,
        }

    # -------------------------------------------------------------------------

    @staticmethod
    def show_summary(context: dict):

        print()

        print("=" * 52)
        print("Deployment Summary")
        print("=" * 52)

        for key, value in context.items():

            print(f"{key:<20}: {value}")

        print("=" * 52)