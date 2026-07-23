"""
===============================================================================
SIRMS Deployment Toolkit

Module : logger.py
Purpose : Console and File Logging
Version : 2.0
===============================================================================
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from colorama import Fore, Style, init

init(autoreset=True)


class Logger:

    def __init__(self, log_directory: str | Path):

        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.log_file = self.log_directory / f"deploy_{timestamp}.log"

        self.logger = logging.getLogger("SIRMS")

        self.logger.setLevel(logging.INFO)

        self.logger.handlers.clear()

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )

        file_handler = logging.FileHandler(
            self.log_file,
            encoding="utf-8",
        )

        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    # ------------------------------------------------------------------

    def _console(self, colour: str, level: str, message: str):

        print(
            colour
            + f"[{datetime.now():%Y-%m-%d %H:%M:%S}] "
            + f"[{level}] {message}"
            + Style.RESET_ALL
        )

    # ------------------------------------------------------------------

    def info(self, message: str):

        self.logger.info(message)
        self._console(Fore.CYAN, "INFO", message)

    # ------------------------------------------------------------------

    def success(self, message: str):

        self.logger.info(message)
        self._console(Fore.GREEN, "SUCCESS", message)

    # ------------------------------------------------------------------

    def warning(self, message: str):

        self.logger.warning(message)
        self._console(Fore.YELLOW, "WARNING", message)

    # ------------------------------------------------------------------

    def error(self, message: str):

        self.logger.error(message)
        self._console(Fore.RED, "ERROR", message)

    # ------------------------------------------------------------------

    def section(self, title: str):

        line = "=" * 80

        print()

        print(Fore.LIGHTBLACK_EX + line)

        print(Fore.WHITE + f"  {title}")

        print(Fore.LIGHTBLACK_EX + line)

        print()

        self.logger.info(line)
        self.logger.info("SECTION : %s", title)
        self.logger.info(line)

    # ------------------------------------------------------------------

    @staticmethod
    def banner():

        print()

        print(Fore.CYAN + "=" * 63)

        print(Fore.GREEN + "             SIRMS Deployment Toolkit v2.0")

        print(Fore.CYAN + "=" * 63)

        print()

    # ------------------------------------------------------------------

    @staticmethod
    def summary(
        *,
        status: str,
        duration: str,
        commit: str,
        backup: str,
    ):

        print()

        print(Fore.CYAN + "=" * 63)

        if status.upper() == "SUCCESS":
            print(Fore.GREEN + "Deployment Completed Successfully")
        else:
            print(Fore.RED + "Deployment Failed")

        print("-" * 63)

        print(f"Duration : {duration}")
        print(f"Commit   : {commit}")
        print(f"Backup   : {backup}")

        print(Fore.CYAN + "=" * 63)

        print()

    # ------------------------------------------------------------------

    @property
    def logfile(self) -> Path:
        return self.log_file