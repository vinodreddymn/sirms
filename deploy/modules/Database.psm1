<#
===============================================================================
SIRMS Deployment Toolkit
Module : Database.psm1
Purpose: PostgreSQL Backup and Restore Operations
Version: 1.0
===============================================================================
#>

Set-StrictMode -Version Latest

function New-DatabaseBackup {
    param(
        [Parameter(Mandatory)][hashtable]$Config,
        [Parameter(Mandatory)][string]$OutputFile
    )

    $env:PGPASSWORD = $Config.LOCAL_DB_PASSWORD
    try {
        & pg_dump `
            -h $Config.LOCAL_DB_HOST `
            -p $Config.LOCAL_DB_PORT `
            -U $Config.LOCAL_DB_USER `
            -F c `
            -f $OutputFile `
            $Config.LOCAL_DB_NAME

        if ($LASTEXITCODE -ne 0) {
            throw "Local database backup failed."
        }

        return $OutputFile
    }
    finally {
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    }
}

function Restore-Database {
    param(
        [Parameter(Mandatory)][hashtable]$Config,
        [Parameter(Mandatory)][string]$BackupFile
    )

    $env:PGPASSWORD = $Config.LOCAL_DB_PASSWORD
    try {
        & psql `
            -h $Config.LOCAL_DB_HOST `
            -p $Config.LOCAL_DB_PORT `
            -U $Config.LOCAL_DB_USER `
            -d postgres `
            -c "DROP DATABASE IF EXISTS $($Config.LOCAL_DB_NAME);"

        & psql `
            -h $Config.LOCAL_DB_HOST `
            -p $Config.LOCAL_DB_PORT `
            -U $Config.LOCAL_DB_USER `
            -d postgres `
            -c "CREATE DATABASE $($Config.LOCAL_DB_NAME);"

        & pg_restore `
            -h $Config.LOCAL_DB_HOST `
            -p $Config.LOCAL_DB_PORT `
            -U $Config.LOCAL_DB_USER `
            -d $Config.LOCAL_DB_NAME `
            --clean `
            --if-exists `
            $BackupFile

        if ($LASTEXITCODE -ne 0) {
            throw "Database restore failed."
        }
    }
    finally {
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    }
}

function Test-BackupFile {
    param([Parameter(Mandatory)][string]$BackupFile)

    if (-not (Test-Path -LiteralPath $BackupFile)) {
        throw "Backup file not found: $BackupFile"
    }

    $item = Get-Item $BackupFile
    if ($item.Length -le 0) {
        throw "Backup file is empty."
    }

    return $true
}

function Get-BackupInfo {
    param([Parameter(Mandatory)][string]$BackupFile)

    $item = Get-Item $BackupFile

    [pscustomobject]@{
        FileName = $item.Name
        FullName = $item.FullName
        SizeBytes = $item.Length
        Created = $item.CreationTime
        Modified = $item.LastWriteTime
    }
}

Export-ModuleMember -Function `
New-DatabaseBackup,`
Restore-Database,`
Test-BackupFile,`
Get-BackupInfo
