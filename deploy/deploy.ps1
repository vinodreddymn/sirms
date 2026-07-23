<#
===============================================================================
SIRMS Deployment Toolkit
File    : deploy.ps1
Purpose : Main Deployment Orchestrator
Version : 1.0
===============================================================================
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Import-Module "$ScriptRoot\modules\Logger.psm1" -Force
Import-Module "$ScriptRoot\modules\Utils.psm1" -Force
Import-Module "$ScriptRoot\modules\Validation.psm1" -Force
Import-Module "$ScriptRoot\modules\Git.psm1" -Force
Import-Module "$ScriptRoot\modules\Database.psm1" -Force
Import-Module "$ScriptRoot\modules\SSH.psm1" -Force
Import-Module "$ScriptRoot\modules\Health.psm1" -Force
Import-Module "$ScriptRoot\modules\Report.psm1" -Force

function Import-EnvFile {
    param([Parameter(Mandatory)][string]$Path)

    $cfg = @{}

    Get-Content $Path | ForEach-Object {

        if($_.Trim().StartsWith("#") -or [string]::IsNullOrWhiteSpace($_)){
            return
        }

        $parts = $_ -split "=",2
        if($parts.Count -eq 2){
            $cfg[$parts[0].Trim()] = $parts[1].Trim()
        }
    }

    return $cfg
}

$config = Import-EnvFile -Path (Join-Path $ScriptRoot ".env")

Initialize-Logger -LogDirectory (Join-Path $ScriptRoot "logs")
Show-Banner

$start = Get-Date

$context = @{
    Status = "FAILED"
    StartTime = $start
    Commit = ""
    Backup = ""
}

try {

    Write-Section "Validation"
    Invoke-Validation -Config $config

    Write-Section "Git"
    $git = Invoke-GitWorkflow `
        -Repository $config.PROJECT_ROOT `
        -CommitMessage ("Deployment {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss")) `
        -Push:($config.AUTO_PUSH -eq "true")

    $context.Commit = $git.Commit

    Write-Section "Database Backup"

    $backupName = "backup_{0}.backup" -f (Get-Timestamp)

    $backupFile = Join-Path `
        (Join-Path $ScriptRoot "backups") `
        $backupName

    New-DirectoryIfMissing (Join-Path $ScriptRoot "backups") | Out-Null

    New-DatabaseBackup `
        -Config $config `
        -OutputFile $backupFile

    $context.Backup = $backupFile

    Write-Section "Upload Backup"

    Copy-FileToRemote `
        -LocalFile $backupFile `
        -RemotePath $config.REMOTE_DEPLOY_DIRECTORY `
        -Host $config.EC2_HOST `
        -User $config.EC2_USER `
        -KeyFile $config.SSH_PRIVATE_KEY `
        -Port ([int]$config.EC2_PORT)

    Write-Section "Remote Deployment"

    $remote = @"
export PROJECT_PATH='$($config.REMOTE_PROJECT_PATH)'
export BACKUP_FILE='$($config.REMOTE_DEPLOY_DIRECTORY)/$backupName'
export DB_NAME='$($config.REMOTE_DB_NAME)'
export DB_USER='$($config.REMOTE_DB_USER)'
export BACKEND_SERVICE='$($config.BACKEND_SERVICE)'
export NGINX_SERVICE='$($config.NGINX_SERVICE)'
bash $($config.REMOTE_DEPLOY_DIRECTORY)/deploy_remote.sh
"@

    Invoke-SshCommand `
        -Host $config.EC2_HOST `
        -User $config.EC2_USER `
        -KeyFile $config.SSH_PRIVATE_KEY `
        -Port ([int]$config.EC2_PORT) `
        -Command $remote

    Write-Section "Health Checks"

    $health = Invoke-HealthChecks -Config $config
    $context.Health = $health

    $context.Status = "SUCCESS"

}
catch {

    Write-ErrorLog $_.Exception.Message

}
finally {

    $end = Get-Date

    $context.EndTime = $end
    $context.Duration = Get-ElapsedTime -Start $start -End $end

    $report = New-DeploymentReport `
        -Context $context `
        -ReportDirectory (Join-Path $ScriptRoot "reports")

    Show-DeploymentReport -Context $context

    Show-Summary `
        -Status $context.Status `
        -Duration $context.Duration `
        -Commit $context.Commit `
        -Backup $context.Backup

    if($context.Status -ne "SUCCESS"){
        exit 1
    }

    exit 0
}
