#!/usr/bin/env bash
###############################################################################
# SIRMS Deployment Toolkit
# File    : deploy_remote.sh
# Purpose : Remote Deployment Engine
# Version : 2.0
###############################################################################

set -Eeuo pipefail

log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*"; }
fail() { log "ERROR: $*"; exit 1; }

PROJECT_PATH="${PROJECT_PATH:?PROJECT_PATH not set}"
BACKUP_FILE="${BACKUP_FILE:-}"
DB_NAME="${DB_NAME:-sirms}"
DB_USER="${DB_USER:-postgres}"
BACKEND_SERVICE="${BACKEND_SERVICE:-sirms-backend}"
NGINX_SERVICE="${NGINX_SERVICE:-nginx}"

log "Starting deployment"

cd "$PROJECT_PATH" || fail "Project path not found: $PROJECT_PATH"

log "Updating source..."
git fetch --all
git pull --ff-only

if [ -d ".venv" ]; then
    log "Activating virtual environment..."
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

if [ -f "backend/requirements.txt" ]; then
    log "Installing Python dependencies..."
    pip install -r backend/requirements.txt
fi

if [ -d "backend" ]; then
    cd backend
    if command -v alembic >/dev/null 2>&1; then
        log "Running Alembic migrations..."
        alembic upgrade head
    fi
    cd ..
fi

if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
    log "Restoring database..."
    dropdb --if-exists -U "$DB_USER" "$DB_NAME" || true
    createdb -U "$DB_USER" "$DB_NAME"
    pg_restore --clean --if-exists -U "$DB_USER" -d "$DB_NAME" "$BACKUP_FILE"
fi

if [ -d "frontend" ]; then
    log "Building frontend..."
    cd frontend
    npm ci
    npm run build
    sudo mkdir -p /var/www/sirms
    sudo rsync -a --delete dist/ /var/www/sirms/
    cd ..
fi

log "Restarting backend..."
sudo systemctl restart "$BACKEND_SERVICE"
sudo systemctl is-active --quiet "$BACKEND_SERVICE" || fail "Backend service failed"

log "Validating Nginx configuration..."
sudo nginx -t

log "Restarting Nginx..."
sudo systemctl restart "$NGINX_SERVICE"
sudo systemctl is-active --quiet "$NGINX_SERVICE" || fail "Nginx service failed"

log "Deployment completed successfully."
