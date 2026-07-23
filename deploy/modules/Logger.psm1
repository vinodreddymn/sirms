<#
===============================================================================
SIRMS Deployment Toolkit
Module : Logger.psm1
Purpose: Console and File Logging
Version: 1.0
===============================================================================
#>

Set-StrictMode -Version Latest

#------------------------------------------------------------------------------
# Module Variables
#------------------------------------------------------------------------------

$script:LogFile = $null

#------------------------------------------------------------------------------
# Initialize Logger
#------------------------------------------------------------------------------

function Initialize-Logger {

    param(
        [Parameter(Mandatory)]
        [string]$LogDirectory
    )

    if (!(Test-Path $LogDirectory)) {

        New-Item `
            -ItemType Directory `
            -Path $LogDirectory `
            -Force | Out-Null

    }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

    $script:LogFile = Join-Path `
        $LogDirectory `
        "deploy_$timestamp.log"

    New-Item `
        -ItemType File `
        -Path $script:LogFile `
        -Force | Out-Null
}

#------------------------------------------------------------------------------
# Internal Writer
#------------------------------------------------------------------------------

function Write-InternalLog {

    param(

        [Parameter(Mandatory)]
        [string]$Level,

        [Parameter(Mandatory)]
        [string]$Message,

        [ConsoleColor]$Color = "White"

    )

    $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    $line = "[{0}] [{1}] {2}" -f `
        $time, `
        $Level, `
        $Message

    Write-Host $line `
        -ForegroundColor $Color

    if ($script:LogFile) {

        Add-Content `
            -Path $script:LogFile `
            -Value $line

    }

}

#------------------------------------------------------------------------------
# Public Logging Functions
#------------------------------------------------------------------------------

function Write-Info {

    param([string]$Message)

    Write-InternalLog `
        -Level "INFO" `
        -Message $Message `
        -Color Cyan

}

function Write-Success {

    param([string]$Message)

    Write-InternalLog `
        -Level "SUCCESS" `
        -Message $Message `
        -Color Green

}

function Write-WarningLog {

    param([string]$Message)

    Write-InternalLog `
        -Level "WARNING" `
        -Message $Message `
        -Color Yellow

}

function Write-ErrorLog {

    param([string]$Message)

    Write-InternalLog `
        -Level "ERROR" `
        -Message $Message `
        -Color Red

}

#------------------------------------------------------------------------------
# Section Header
#------------------------------------------------------------------------------

function Write-Section {

    param(
        [Parameter(Mandatory)]
        [string]$Title
    )

    $line = "=" * 80

    Write-Host ""
    Write-Host $line -ForegroundColor DarkGray
    Write-Host ("  {0}" -f $Title) -ForegroundColor White
    Write-Host $line -ForegroundColor DarkGray
    Write-Host ""

    if ($script:LogFile) {

        Add-Content `
            -Path $script:LogFile `
            -Value ""

        Add-Content `
            -Path $script:LogFile `
            -Value $line

        Add-Content `
            -Path $script:LogFile `
            -Value ("SECTION : {0}" -f $Title)

        Add-Content `
            -Path $script:LogFile `
            -Value $line

    }

}

#------------------------------------------------------------------------------
# Banner
#------------------------------------------------------------------------------

function Show-Banner {

    Clear-Host

    Write-Host ""
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host "             SIRMS Deployment Toolkit v1.0" -ForegroundColor Green
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host ""

}

#------------------------------------------------------------------------------
# Summary
#------------------------------------------------------------------------------

function Show-Summary {

    param(

        [Parameter(Mandatory)]
        [string]$Status,

        [Parameter(Mandatory)]
        [string]$Duration,

        [Parameter(Mandatory)]
        [string]$Commit,

        [Parameter(Mandatory)]
        [string]$Backup

    )

    Write-Host ""

    Write-Host "===============================================================" `
        -ForegroundColor Cyan

    if ($Status -eq "SUCCESS") {

        Write-Host "Deployment Completed Successfully" `
            -ForegroundColor Green

    }
    else {

        Write-Host "Deployment Failed" `
            -ForegroundColor Red

    }

    Write-Host "---------------------------------------------------------------"

    Write-Host ("Duration : {0}" -f $Duration)

    Write-Host ("Commit   : {0}" -f $Commit)

    Write-Host ("Backup   : {0}" -f $Backup)

    Write-Host "===============================================================" `
        -ForegroundColor Cyan

}

#------------------------------------------------------------------------------
# Get Log File
#------------------------------------------------------------------------------

function Get-LogFile {

    return $script:LogFile

}

#------------------------------------------------------------------------------
# Module Export
#------------------------------------------------------------------------------

Export-ModuleMember `
    -Function Initialize-Logger,
              Write-Info,
              Write-Success,
              Write-WarningLog,
              Write-ErrorLog,
              Write-Section,
              Show-Banner,
              Show-Summary,
              Get-LogFile