<#
===============================================================================
SIRMS Deployment Toolkit
Module : Validation.psm1
Purpose: Environment Validation
Version: 1.0
===============================================================================
#>

Set-StrictMode -Version Latest

function Test-RequiredDirectory {
    param([Parameter(Mandatory)][string]$Path)
    if(-not (Test-Path -LiteralPath $Path)){
        throw "Required directory not found: $Path"
    }
}

function Test-RequiredFile {
    param([Parameter(Mandatory)][string]$Path)
    if(-not (Test-Path -LiteralPath $Path)){
        throw "Required file not found: $Path"
    }
}

function Test-RequiredCommand {
    param([Parameter(Mandatory)][string]$Command)
    if(-not (Get-Command $Command -ErrorAction SilentlyContinue)){
        throw "Required command not available: $Command"
    }
}

function Test-GitRepository {
    param([Parameter(Mandatory)][string]$ProjectRoot)
    Test-RequiredDirectory $ProjectRoot
    Test-RequiredDirectory (Join-Path $ProjectRoot ".git")
}

function Test-SshKey {
    param([Parameter(Mandatory)][string]$KeyPath)
    Test-RequiredFile $KeyPath
}

function Test-PostgresClient {
    Test-RequiredCommand "pg_dump"
    Test-RequiredCommand "psql"
}

function Test-DevelopmentTools {
    foreach($cmd in @("git","ssh","scp","python","node","npm")){
        Test-RequiredCommand $cmd
    }
}

function Test-ProjectStructure {
    param([Parameter(Mandatory)][string]$ProjectRoot)
    $required = @(
        "backend",
        "frontend",
        "database",
        "deploy"
    )
    foreach($item in $required){
        Test-RequiredDirectory (Join-Path $ProjectRoot $item)
    }
}

function Test-DatabaseConnection {
    param(
        [Parameter(Mandatory)][string]$Host,
        [Parameter(Mandatory)][int]$Port,
        [Parameter(Mandatory)][string]$Database,
        [Parameter(Mandatory)][string]$User,
        [Parameter(Mandatory)][string]$Password
    )

    $env:PGPASSWORD = $Password
    try{
        & psql -h $Host -p $Port -U $User -d $Database -c "SELECT 1;" | Out-Null
        if($LASTEXITCODE -ne 0){
            throw "Unable to connect to PostgreSQL."
        }
    }
    finally{
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    }
}

function Invoke-Validation {
    param([Parameter(Mandatory)][hashtable]$Config)

    Test-DevelopmentTools
    Test-GitRepository $Config.PROJECT_ROOT
    Test-ProjectStructure $Config.PROJECT_ROOT
    Test-SshKey $Config.SSH_PRIVATE_KEY
    Test-PostgresClient
    Test-DatabaseConnection `
        -Host $Config.LOCAL_DB_HOST `
        -Port ([int]$Config.LOCAL_DB_PORT) `
        -Database $Config.LOCAL_DB_NAME `
        -User $Config.LOCAL_DB_USER `
        -Password $Config.LOCAL_DB_PASSWORD

    return $true
}

Export-ModuleMember -Function `
Test-RequiredDirectory,`
Test-RequiredFile,`
Test-RequiredCommand,`
Test-GitRepository,`
Test-SshKey,`
Test-PostgresClient,`
Test-DevelopmentTools,`
Test-ProjectStructure,`
Test-DatabaseConnection,`
Invoke-Validation
