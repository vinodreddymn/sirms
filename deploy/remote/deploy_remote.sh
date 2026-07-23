#!/usr/bin/env bash
###############################################################################
# SIRMS Deployment Toolkit
# File    : deploy_remote.sh
# Purpose : Remote deployment on Ubuntu
# Version : 1.0
###############################################################################

set -euo pipefail

PROJECT_PATH="${PROJECT_PATH:-/home/ubuntu/projects/sirms}"
BACKUP_FILE="${BACKUP_FILE:-}"
DB_NAME="${DB_NAME:-sirms}"
DB_USER="${DB_USER:-svr_user}"
BACKEND_SERVICE="${BACKEND_SERVICE:-sirms-backend}"
NGINX_SERVICE="${NGINX_SERVICE:-nginx}"

cd "$PROJECT_PATH"

echo "Updating source..."
git pull --ff-only

if [[ -n "$BACKUP_FILE" && -f "$BACKUP_FILE" ]]; then
    echo "Restoring database..."
    dropdb --if-exists -U "$DB_USER" "$DB_NAME" || true
    createdb -U "$DB_USER" "$DB_NAME"
    pg_restore --clean --if-exists -U "$DB_USER" -d "$DB_NAME" "$BACKUP_FILE"
fi

if [[ -d ".venv" ]]; then
    source .venv/bin/activate
fi

if [[ -f "backend/requirements.txt" ]]; then
    pip install -r backend/requirements.txt
fi

if [[ -d "backend" ]]; then
    cd backend
    if command -v alembic >/dev/null 2>&1; then
        alembic upgrade head
    fi
    cd ..
fi

sudo systemctl restart "$BACKEND_SERVICE"

if [[ -d "frontend" ]]; then
    cd frontend
    npm install
    npm run build
    sudo mkdir -p /var/www/sirms
    sudo cp -r dist/* /var/www/sirms/
    cd ..
fi

sudo systemctl restart "$NGINX_SERVICE"

echo "Deployment completed successfully."
