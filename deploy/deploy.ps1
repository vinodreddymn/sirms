<#
===============================================================================
SIRMS Deployment Toolkit
File    : deploy.ps1
Purpose : Main Deployment Orchestrator
Version : 2.0
===============================================================================
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptRoot = Split-Path -Parent $PSCommandPath

foreach($m in "Logger","Utils","Validation","Git","Database","SSH","Health","Report"){
    Import-Module (Join-Path $ScriptRoot "modules\$m.psm1") -Force
}

function Import-EnvFile {
    param([Parameter(Mandatory)][string]$Path)
    if(!(Test-Path $Path)){ throw ".env not found: $Path" }
    $cfg=@{}
    foreach($line in Get-Content $Path){
        $line=$line.Trim()
        if(!$line -or $line.StartsWith("#")){ continue }
        $k,$v=$line -split "=",2
        if($null -ne $v){
            $cfg[$k.Trim()]=$v.Trim().Trim("'`"")
        }
    }
    $cfg
}

$config = Import-EnvFile (Join-Path $ScriptRoot ".env")

Initialize-Logger -LogDirectory (Join-Path $ScriptRoot "logs")
Show-Banner

$start=Get-Date
$ctx=@{
    Status="FAILED"
    StartTime=$start
    Commit=""
    Backup=""
    Health=$null
}

try{
    Write-Section "Validation"
    Invoke-Validation -Config $config | Out-Null

    Write-Section "Git"
    $git=Invoke-GitWorkflow `
        -Repository $config.PROJECT_ROOT `
        -CommitMessage ("Deployment {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss")) `
        -Push:($config.AUTO_PUSH -eq "true")
    $ctx.Commit=$git.Commit

    Write-Section "Database Backup"
    $backupDir=Join-Path $ScriptRoot "backups"
    New-DirectoryIfMissing $backupDir | Out-Null
    $backupName="backup_{0}.backup" -f (Get-Timestamp)
    $backupFile=Join-Path $backupDir $backupName
    New-DatabaseBackup -Config $config -OutputFile $backupFile
    $ctx.Backup=$backupFile

    Write-Section "Prepare Remote"
    Ensure-RemoteDirectory `
        -Host $config.EC2_HOST `
        -User $config.EC2_USER `
        -KeyFile $config.SSH_PRIVATE_KEY `
        -Port ([int]$config.EC2_PORT) `
        -Directory $config.REMOTE_DEPLOY_DIRECTORY

    Write-Section "Upload Files"
    $remoteScript=Join-Path $ScriptRoot "remote\deploy_remote.sh"
    if(!(Test-Path $remoteScript)){ throw "Missing $remoteScript" }

    Copy-FileToRemote `
        -LocalFile $remoteScript `
        -RemotePath $config.REMOTE_DEPLOY_DIRECTORY `
        -Host $config.EC2_HOST `
        -User $config.EC2_USER `
        -KeyFile $config.SSH_PRIVATE_KEY `
        -Port ([int]$config.EC2_PORT)

    Copy-FileToRemote `
        -LocalFile $backupFile `
        -RemotePath $config.REMOTE_DEPLOY_DIRECTORY `
        -Host $config.EC2_HOST `
        -User $config.EC2_USER `
        -KeyFile $config.SSH_PRIVATE_KEY `
        -Port ([int]$config.EC2_PORT)

    Write-Section "Remote Deployment"

    $remote = @"
chmod +x "$($config.REMOTE_DEPLOY_DIRECTORY)/deploy_remote.sh"

export PROJECT_PATH="$($config.REMOTE_PROJECT_PATH)"
export BACKUP_FILE="$($config.REMOTE_DEPLOY_DIRECTORY)/$backupName"
export DB_NAME="$($config.REMOTE_DB_NAME)"
export DB_USER="$($config.REMOTE_DB_USER)"
export BACKEND_SERVICE="$($config.BACKEND_SERVICE)"
export NGINX_SERVICE="$($config.NGINX_SERVICE)"

bash "$($config.REMOTE_DEPLOY_DIRECTORY)/deploy_remote.sh"
"@

    Invoke-SshCommand `
        -Host $config.EC2_HOST `
        -User $config.EC2_USER `
        -KeyFile $config.SSH_PRIVATE_KEY `
        -Port ([int]$config.EC2_PORT) `
        -Command $remote

    if($config.ENABLE_HEALTH_CHECK -eq "true"){
        Write-Section "Health Checks"
        $ctx.Health=Invoke-HealthChecks -Config $config
    }

    $ctx.Status="SUCCESS"
}
catch{
    Write-ErrorLog $_.Exception.ToString()
}
finally{
    $end=Get-Date
    $ctx.EndTime=$end
    $ctx.Duration=Get-ElapsedTime -Start $start -End $end

    $reportDir=Join-Path $ScriptRoot "reports"
    New-DirectoryIfMissing $reportDir | Out-Null

    $null=New-DeploymentReport -Context $ctx -ReportDirectory $reportDir
    Show-DeploymentReport -Context $ctx
    Show-Summary `
        -Status $ctx.Status `
        -Duration $ctx.Duration `
        -Commit $ctx.Commit `
        -Backup $ctx.Backup

    if($ctx.Status -eq "SUCCESS"){ exit 0 } else { exit 1 }
}
