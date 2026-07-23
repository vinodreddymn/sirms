<#
===============================================================================
SIRMS Deployment Toolkit
Module : Utils.psm1
Purpose: Common Utility Functions
Version: 1.0
===============================================================================
#>

Set-StrictMode -Version Latest

function Get-Timestamp {
    param([string]$Format = "yyyyMMdd_HHmmss")
    (Get-Date).ToString($Format)
}

function New-DirectoryIfMissing {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
    (Resolve-Path $Path).Path
}

function Test-CommandExists {
    param([Parameter(Mandatory)][string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Invoke-Process {
    param(
        [Parameter(Mandatory)][string]$FilePath,
        [string[]]$Arguments = @(),
        [string]$WorkingDirectory = (Get-Location).Path,
        [switch]$IgnoreExitCode
    )

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $FilePath
    foreach($a in $Arguments){ [void]$psi.ArgumentList.Add($a) }
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true

    $p = [System.Diagnostics.Process]::new()
    $p.StartInfo = $psi
    [void]$p.Start()
    $out = $p.StandardOutput.ReadToEnd()
    $err = $p.StandardError.ReadToEnd()
    $p.WaitForExit()

    if((-not $IgnoreExitCode) -and $p.ExitCode -ne 0){
        throw "Process failed: $FilePath`n$err"
    }

    [pscustomobject]@{
        ExitCode = $p.ExitCode
        StdOut = $out.TrimEnd()
        StdErr = $err.TrimEnd()
        Success = ($p.ExitCode -eq 0)
    }
}

function Get-ElapsedTime {
    param([datetime]$Start,[datetime]$End)
    $ts = $End - $Start
    "{0:00}:{1:00}:{2:00}" -f [int]$ts.TotalHours,$ts.Minutes,$ts.Seconds
}

function Get-FileChecksum {
    param([Parameter(Mandatory)][string]$Path)
    (Get-FileHash -Path $Path -Algorithm SHA256).Hash
}

function Remove-OldFiles {
    param(
        [Parameter(Mandatory)][string]$Directory,
        [Parameter(Mandatory)][int]$Keep,
        [string]$Filter="*"
    )

    if(!(Test-Path $Directory)){ return }

    Get-ChildItem $Directory -File -Filter $Filter |
        Sort-Object LastWriteTime -Descending |
        Select-Object -Skip $Keep |
        Remove-Item -Force
}

function Test-IsAdministrator {
    $id=[Security.Principal.WindowsIdentity]::GetCurrent()
    $p=[Security.Principal.WindowsPrincipal]::new($id)
    $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Resolve-AbsolutePath {
    param([Parameter(Mandatory)][string]$Path)
    [IO.Path]::GetFullPath($Path)
}

Export-ModuleMember -Function `
Get-Timestamp,New-DirectoryIfMissing,Test-CommandExists,Invoke-Process,`
Get-ElapsedTime,Get-FileChecksum,Remove-OldFiles,`
Test-IsAdministrator,Resolve-AbsolutePath
