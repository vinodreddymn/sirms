<#
===============================================================================
SIRMS Deployment Toolkit
Module : Git.psm1
Purpose: Git Operations
Version: 1.0
===============================================================================
#>

Set-StrictMode -Version Latest

function Test-GitClean {
    param([Parameter(Mandatory)][string]$Repository)

    Push-Location $Repository
    try {
        $status = git status --porcelain
        return [string]::IsNullOrWhiteSpace(($status | Out-String))
    }
    finally { Pop-Location }
}

function Get-CurrentBranch {
    param([Parameter(Mandatory)][string]$Repository)
    Push-Location $Repository
    try { (git branch --show-current).Trim() }
    finally { Pop-Location }
}

function Get-CurrentCommit {
    param([Parameter(Mandatory)][string]$Repository)
    Push-Location $Repository
    try { (git rev-parse --short HEAD).Trim() }
    finally { Pop-Location }
}

function Invoke-GitAdd {
    param([Parameter(Mandatory)][string]$Repository)
    Push-Location $Repository
    try {
        git add .
        if($LASTEXITCODE -ne 0){ throw "git add failed." }
    }
    finally { Pop-Location }
}

function Invoke-GitCommit {
    param(
        [Parameter(Mandatory)][string]$Repository,
        [Parameter(Mandatory)][string]$Message
    )
    Push-Location $Repository
    try {
        $pending = git status --porcelain
        if([string]::IsNullOrWhiteSpace(($pending|Out-String))){
            return $false
        }

        git commit -m $Message
        if($LASTEXITCODE -ne 0){ throw "git commit failed." }
        return $true
    }
    finally { Pop-Location }
}

function Invoke-GitPush {
    param([Parameter(Mandatory)][string]$Repository)

    Push-Location $Repository
    try {
        git push
        if($LASTEXITCODE -ne 0){ throw "git push failed." }
    }
    finally { Pop-Location }
}

function Invoke-GitPull {
    param([Parameter(Mandatory)][string]$Repository)

    Push-Location $Repository
    try {
        git pull --ff-only
        if($LASTEXITCODE -ne 0){ throw "git pull failed." }
    }
    finally { Pop-Location }
}

function Invoke-GitWorkflow {
    param(
        [Parameter(Mandatory)][string]$Repository,
        [Parameter(Mandatory)][string]$CommitMessage,
        [switch]$Push
    )

    Invoke-GitAdd -Repository $Repository
    $committed = Invoke-GitCommit -Repository $Repository -Message $CommitMessage

    if($Push){
        Invoke-GitPush -Repository $Repository
    }

    [pscustomobject]@{
        Branch = Get-CurrentBranch -Repository $Repository
        Commit = Get-CurrentCommit -Repository $Repository
        Committed = $committed
    }
}

Export-ModuleMember -Function `
Test-GitClean,`
Get-CurrentBranch,`
Get-CurrentCommit,`
Invoke-GitAdd,`
Invoke-GitCommit,`
Invoke-GitPush,`
Invoke-GitPull,`
Invoke-GitWorkflow
