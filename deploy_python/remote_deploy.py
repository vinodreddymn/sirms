
"""
SIRMS Deployment Toolkit
Module : remote_deploy.py
Purpose: Remote Deployment Orchestrator
Version: 3.0
"""

from __future__ import annotations

class RemoteDeploymentError(Exception):
    pass

class RemoteDeployment:
    def __init__(self, ssh, config: dict, logger=None):
        self.ssh=ssh
        self.config=config
        self.logger=logger
        self.project_path=config["PROJECT_PATH"]
        self.backend_service=config.get("BACKEND_SERVICE","sirms-backend")
        self.nginx_service=config.get("NGINX_SERVICE","nginx")
        self.db_name=config.get("LOCAL_DB_NAME","sirms")
        self.db_user=config.get("LOCAL_DB_USER","postgres")

    def _log(self,msg):
        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)

    def _run(self,cmd):
        self._log(cmd)
        return self.ssh.execute(cmd)

    def _cd(self,cmd):
        return self._run(f"cd '{self.project_path}' && {cmd}")

    def update_source(self):
        self._cd("git fetch --all")
        self._cd("git pull --ff-only")

    def install_dependencies(self):
        self._cd("if [ -d .venv ]; then . .venv/bin/activate; fi && "
                 "if [ -f backend/requirements.txt ]; then pip install -r backend/requirements.txt; fi")

    def migrate_database(self):
        self._cd("if [ -d backend ] && command -v alembic >/dev/null 2>&1; then cd backend && alembic upgrade head; fi")

    def restore_database(self,backup_file=None):
        if not backup_file:
            return
        self._run(
            f"dropdb --if-exists -U {self.db_user} {self.db_name} || true && "
            f"createdb -U {self.db_user} {self.db_name} && "
            f"pg_restore --clean --if-exists -U {self.db_user} -d {self.db_name} '{backup_file}'"
        )

    def build_frontend(self):
        self._cd("if [ -d frontend ]; then cd frontend && npm ci && npm run build; fi")

    def deploy_frontend(self):
        self._run(
            "sudo mkdir -p /var/www/sirms && "
            f"sudo rsync -a --delete '{self.project_path}/frontend/dist/' /var/www/sirms/"
        )

    def restart_backend(self):
        self._run(f"sudo systemctl restart {self.backend_service}")
        self._run(f"sudo systemctl is-active --quiet {self.backend_service}")

    def validate_nginx(self):
        self._run("sudo nginx -t")

    def restart_nginx(self):
        self._run(f"sudo systemctl restart {self.nginx_service}")
        self._run(f"sudo systemctl is-active --quiet {self.nginx_service}")

    def verify(self):
        self._run("echo Deployment completed successfully.")

    def deploy(self,backup_file=None):
        try:
            self.update_source()
            self.install_dependencies()
            self.migrate_database()
            self.restore_database(backup_file)
            self.build_frontend()
            self.deploy_frontend()
            self.restart_backend()
            self.validate_nginx()
            self.restart_nginx()
            self.verify()
        except Exception as exc:
            raise RemoteDeploymentError(str(exc)) from exc
