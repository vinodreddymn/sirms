# SIRMS Deployment Toolkit

## Version

**Version:** 1.0

---

## Overview

The SIRMS Deployment Toolkit automates deployment of the SIRMS application from a Windows development machine to the AWS EC2 server.

The toolkit performs the complete deployment process with a single command.

```powershell
.\deploy.ps1
```

---

# Features

* Automatic Git commit
* Automatic Git push
* PostgreSQL database backup
* Secure backup upload to EC2
* Remote database restore
* Source code synchronization
* Backend restart
* Frontend build
* Nginx deployment
* Health checks
* Deployment logging
* Deployment reports
* Automatic backup retention

---

# Project Structure

```
deploy/
│
├── deploy.ps1
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── modules/
│   ├── Logger.psm1
│   ├── Utils.psm1
│   ├── Validation.psm1
│   ├── Git.psm1
│   ├── Database.psm1
│   ├── SSH.psm1
│   ├── Health.psm1
│   └── Report.psm1
│
├── remote/
│   └── deploy_remote.sh
│
├── backups/
├── logs/
└── reports/
```

---

# Prerequisites

## Local Machine

* Windows 11
* PowerShell 7+
* Git
* PostgreSQL Client Tools
* SSH Client
* Node.js
* npm
* Python
* VS Code

## Remote Server

* Ubuntu
* PostgreSQL
* FastAPI
* Nginx
* Git
* Python Virtual Environment

---

# Initial Setup

Copy the example configuration file.

```
copy .env.example .env
```

Update all values inside `.env`.

---

# Deployment Process

The deployment performs the following steps.

1. Load configuration.
2. Validate environment.
3. Commit source code.
4. Push to GitHub.
5. Create PostgreSQL backup.
6. Upload backup to EC2.
7. Connect to EC2.
8. Stop backend service.
9. Backup remote database.
10. Restore uploaded database.
11. Pull latest source code.
12. Install dependencies.
13. Run Alembic migrations.
14. Restart backend.
15. Build frontend.
16. Deploy frontend to Nginx.
17. Restart Nginx.
18. Execute health checks.
19. Generate deployment report.
20. Finish deployment.

---

# Running Deployment

Execute the deployment from the project root.

```powershell
.\deploy\deploy.ps1
```

---

# Log Files

Deployment logs are stored in:

```
deploy/logs/
```

Each deployment creates a timestamped log file.

---

# Reports

Deployment reports are stored in:

```
deploy/reports/
```

Each report contains:

* Deployment status
* Start time
* End time
* Duration
* Git commit
* Backup file
* Health check results

---

# Backups

Local database backups are stored in:

```
deploy/backups/
```

Remote backups are stored on the EC2 server.

The toolkit automatically retains only the configured number of recent backups.

---

# Failure Handling

If any deployment step fails:

* Deployment stops immediately.
* The error is logged.
* A deployment summary is generated.
* No further deployment actions are executed.

---

# Security

* Never commit the `.env` file.
* Keep the SSH private key secure.
* Restrict access to deployment logs.
* Protect PostgreSQL credentials.

---

# Version 1 Scope

Version 1 includes:

* Automated deployment
* Database synchronization
* Source code synchronization
* Backend deployment
* Frontend deployment
* Health verification
* Logging
* Reporting

Future enhancements will be introduced in later versions without changing the Version 1 deployment workflow.

---

# License

This deployment toolkit is part of the SIRMS project and is intended for internal development and deployment.
