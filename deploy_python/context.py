
from __future__ import annotations

from pathlib import Path

from config import Config
from logger import Logger
from validation import ValidationManager
from git_manager import GitManager
from database import DatabaseManager
from ssh_manager import SSHManager
from health import HealthManager
from report import ReportManager
from remote.remote_deploy import RemoteDeployment

class DeploymentContext:
    def __init__(self, config: Config, root: str | Path):
        self.config = config
        self.root = Path(root)

        self.logger = Logger(self.root / "logs")
        self.validator = ValidationManager(config.__dict__)
        self.git = GitManager(config.project_root)
        self.database = DatabaseManager({
            "LOCAL_DB_HOST": config.local_db_host,
            "LOCAL_DB_PORT": config.local_db_port,
            "LOCAL_DB_USER": config.local_db_user,
            "LOCAL_DB_PASSWORD": config.local_db_password,
            "LOCAL_DB_NAME": config.local_db_name,
        })
        self.ssh = SSHManager(
            host=config.ec2_host,
            user=config.ec2_user,
            key_file=config.ssh_private_key,
            port=config.ec2_port,
        )
        self.health = HealthManager({
            "BACKEND_HEALTH_URL": config.backend_health_url,
            "FRONTEND_HEALTH_URL": config.frontend_health_url,
        })
        self.report = ReportManager(self.root / "reports")
        self.remote = RemoteDeployment(
            ssh=self.ssh,
            logger=self.logger,
            config={
                "PROJECT_PATH": config.remote_project_path,
                "BACKEND_SERVICE": config.backend_service,
                "NGINX_SERVICE": config.nginx_service,
                "LOCAL_DB_NAME": config.remote_db_name,
                "LOCAL_DB_USER": config.remote_db_user,
            },
        )
