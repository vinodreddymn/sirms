
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from dotenv import dotenv_values

from exceptions import ConfigurationError

def _to_bool(v: str | None, default=False) -> bool:
    if v is None:
        return default
    return str(v).strip().lower() in {"1","true","yes","on"}

@dataclass(frozen=True)
class Config:
    project_root: Path
    ssh_private_key: Path
    ec2_host: str
    ec2_user: str
    ec2_port: int
    remote_project_path: str
    remote_deploy_directory: str
    backend_service: str
    nginx_service: str
    local_db_host: str
    local_db_port: int
    local_db_name: str
    local_db_user: str
    local_db_password: str
    remote_db_name: str
    remote_db_user: str
    backend_health_url: str
    frontend_health_url: str
    auto_push: bool
    enable_health_check: bool

    def __getitem__(self,key):
        return getattr(self,key.lower())

def load_config(env_file: str | Path) -> Config:
    env = dotenv_values(env_file)
    required = [
        "PROJECT_ROOT","SSH_PRIVATE_KEY","EC2_HOST","EC2_USER",
        "REMOTE_PROJECT_PATH","REMOTE_DEPLOY_DIRECTORY",
        "LOCAL_DB_HOST","LOCAL_DB_PORT","LOCAL_DB_NAME",
        "LOCAL_DB_USER","LOCAL_DB_PASSWORD"
    ]
    missing=[k for k in required if not env.get(k)]
    if missing:
        raise ConfigurationError(f"Missing required .env variables: {', '.join(missing)}")
    return Config(
        project_root=Path(env["PROJECT_ROOT"]).expanduser().resolve(),
        ssh_private_key=Path(env["SSH_PRIVATE_KEY"]).expanduser().resolve(),
        ec2_host=env["EC2_HOST"],
        ec2_user=env["EC2_USER"],
        ec2_port=int(env.get("EC2_PORT",22)),
        remote_project_path=env["REMOTE_PROJECT_PATH"],
        remote_deploy_directory=env["REMOTE_DEPLOY_DIRECTORY"],
        backend_service=env.get("BACKEND_SERVICE","sirms-backend"),
        nginx_service=env.get("NGINX_SERVICE","nginx"),
        local_db_host=env["LOCAL_DB_HOST"],
        local_db_port=int(env["LOCAL_DB_PORT"]),
        local_db_name=env["LOCAL_DB_NAME"],
        local_db_user=env["LOCAL_DB_USER"],
        local_db_password=env["LOCAL_DB_PASSWORD"],
        remote_db_name=env.get("REMOTE_DB_NAME",env["LOCAL_DB_NAME"]),
        remote_db_user=env.get("REMOTE_DB_USER",env["LOCAL_DB_USER"]),
        backend_health_url=env.get("BACKEND_HEALTH_URL",""),
        frontend_health_url=env.get("FRONTEND_HEALTH_URL",""),
        auto_push=_to_bool(env.get("AUTO_PUSH")),
        enable_health_check=_to_bool(env.get("ENABLE_HEALTH_CHECK")),
    )
