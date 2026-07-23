"""
===============================================================================
SIRMS Deployment Toolkit

File    : deploy.py
Purpose : Main Deployment Orchestrator
Version : 4.0
===============================================================================
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from config import load_config
from database import DatabaseManager
from exceptions import DeploymentError
from git_manager import GitManager
from health import HealthManager
from logger import Logger
from remote_deploy import RemoteDeployment
from report import ReportManager
from ssh_manager import SSHManager
from utils import (
    ensure_directory,
    get_elapsed_time,
    get_timestamp,
)
from validation import ValidationManager


def main() -> int:
    """
    Main deployment workflow.
    """

    script_root = Path(__file__).resolve().parent

    # ------------------------------------------------------------------
    # Load configuration
    # ------------------------------------------------------------------

    config = load_config(script_root / ".env")

    # ------------------------------------------------------------------
    # Logger
    # ------------------------------------------------------------------

    logger = Logger(script_root / "logs")
    logger.banner()

    start = datetime.now()

    context = {
        "Status": "FAILED",
        "StartTime": start.isoformat(),
        "Commit": "",
        "Backup": "",
        "Health": None,
    }

    try:

        # ==============================================================
        # Validation
        # ==============================================================

        logger.section("Validation")

        ValidationManager(config).run()

        # ==============================================================
        # Git
        # ==============================================================

        logger.section("Git")

        git = GitManager(config.project_root)

        git_result = git.workflow(
            commit_message=f"Deployment {datetime.now():%Y-%m-%d %H:%M:%S}",
            push=config.auto_push,
        )

        context["Commit"] = git_result.commit

        # ==============================================================
        # Database Backup
        # ==============================================================

        logger.section("Database Backup")

        backup_dir = ensure_directory(script_root / "backups")

        backup_name = f"backup_{get_timestamp()}.backup"

        backup_file = backup_dir / backup_name

        database = DatabaseManager(config)

        database.backup(backup_file)

        context["Backup"] = str(backup_file)

        # ==============================================================
        # Remote Deployment
        # ==============================================================

        logger.section("Remote Deployment")

        with SSHManager(
            host=config.ec2_host,
            user=config.ec2_user,
            key_file=config.ssh_private_key,
            port=config.ec2_port,
        ) as ssh:

            logger.info("Uploading database backup...")

            ssh.upload(
                backup_file,
                config.remote_deploy_directory,
            )

            remote = RemoteDeployment(
                ssh=ssh,
                logger=logger,
                config={
                    "PROJECT_PATH": config.remote_project_path,
                    "BACKEND_SERVICE": config.backend_service,
                    "NGINX_SERVICE": config.nginx_service,
                    "LOCAL_DB_NAME": config.remote_db_name,
                    "LOCAL_DB_USER": config.remote_db_user,
                },
            )

            remote.deploy(
                backup_file=f"{config.remote_deploy_directory}/{backup_name}"
            )

        # ==============================================================
        # Health Checks
        # ==============================================================

        if config.enable_health_check:

            logger.section("Health Checks")

            health = HealthManager(config)

            context["Health"] = health.run().to_dict()

        context["Status"] = "SUCCESS"

    except DeploymentError as ex:

        logger.error(str(ex))

    except Exception as ex:

        logger.error(f"Unexpected Error: {ex}")

    finally:

        end = datetime.now()

        context["EndTime"] = end.isoformat()

        context["Duration"] = get_elapsed_time(start, end)

        report_dir = ensure_directory(script_root / "reports")

        report_manager = ReportManager(report_dir)

        reports = report_manager.create(context)

        report_manager.show_summary(context)

        logger.summary(
            status=context["Status"],
            duration=context["Duration"],
            commit=context["Commit"],
            backup=context["Backup"],
        )

        logger.info(f"JSON Report : {reports['json']}")
        logger.info(f"HTML Report : {reports['html']}")

    return 0 if context["Status"] == "SUCCESS" else 1


if __name__ == "__main__":
    sys.exit(main())