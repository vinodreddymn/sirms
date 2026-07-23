<#
===============================================================================
SIRMS Deployment Toolkit
Module : SSH.psm1
Purpose: SSH and SCP Operations
Version: 1.0
===============================================================================
#>

Set-StrictMode -Version Latest

function Invoke-SshCommand {
    param(
        [Parameter(Mandatory)][string]$Host,
        [Parameter(Mandatory)][string]$User,
        [Parameter(Mandatory)][string]$KeyFile,
        [Parameter(Mandatory)][string]$Command,
        [int]$Port = 22
    )

    & ssh -i $KeyFile -p $Port -o StrictHostKeyChecking=no "$User@$Host" $Command

    if($LASTEXITCODE -ne 0){
        throw "SSH command failed."
    }
}

function Copy-FileToRemote {
    param(
        [Parameter(Mandatory)][string]$LocalFile,
        [Parameter(Mandatory)][string]$RemotePath,
        [Parameter(Mandatory)][string]$Host,
        [Parameter(Mandatory)][string]$User,
        [Parameter(Mandatory)][string]$KeyFile,
        [int]$Port = 22
    )

    & scp -i $KeyFile -P $Port -o StrictHostKeyChecking=no `
        $LocalFile "$User@$Host`:$RemotePath"

    if($LASTEXITCODE -ne 0){
        throw "SCP upload failed."
    }
}

function Copy-FileFromRemote {
    param(
        [Parameter(Mandatory)][string]$RemoteFile,
        [Parameter(Mandatory)][string]$LocalPath,
        [Parameter(Mandatory)][string]$Host,
        [Parameter(Mandatory)][string]$User,
        [Parameter(Mandatory)][string]$KeyFile,
        [int]$Port = 22
    )

    & scp -i $KeyFile -P $Port -o StrictHostKeyChecking=no `
        "$User@$Host`:$RemoteFile" $LocalPath

    if($LASTEXITCODE -ne 0){
        throw "SCP download failed."
    }
}

function Test-SshConnection {
    param(
        [Parameter(Mandatory)][string]$Host,
        [Parameter(Mandatory)][string]$User,
        [Parameter(Mandatory)][string]$KeyFile,
        [int]$Port = 22
    )

    try{
        Invoke-SshCommand -Host $Host -User $User -KeyFile $KeyFile -Port $Port -Command "echo connected"
        return $true
    }
    catch{
        return $false
    }
}

Export-ModuleMember -Function `
Invoke-SshCommand,`
Copy-FileToRemote,`
Copy-FileFromRemote,`
Test-SshConnection
