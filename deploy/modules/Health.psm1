<#
===============================================================================
SIRMS Deployment Toolkit
Module : Health.psm1
Purpose: Health Check Operations
Version : 1.0
===============================================================================
#>

Set-StrictMode -Version Latest

function Test-HttpEndpoint {
    param(
        [Parameter(Mandatory)][string]$Url,
        [int]$TimeoutSeconds = 15
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec $TimeoutSeconds -UseBasicParsing
        [pscustomobject]@{
            Url = $Url
            Success = ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300)
            StatusCode = $response.StatusCode
        }
    }
    catch {
        [pscustomobject]@{
            Url = $Url
            Success = $false
            StatusCode = $null
            Error = $_.Exception.Message
        }
    }
}

function Test-TcpPort {
    param(
        [Parameter(Mandatory)][string]$Host,
        [Parameter(Mandatory)][int]$Port
    )

    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $task = $client.ConnectAsync($Host,$Port)
        if(-not $task.Wait(3000)){ return $false }
        return $client.Connected
    }
    catch {
        return $false
    }
    finally {
        $client.Dispose()
    }
}

function Test-DiskSpace {
    param([string]$Drive="C")
    $disk = Get-CimInstance Win32_LogicalDisk -Filter ("DeviceID='{0}:'" -f $Drive)
    [pscustomobject]@{
        Drive=$Drive
        FreeGB=[math]::Round($disk.FreeSpace/1GB,2)
        TotalGB=[math]::Round($disk.Size/1GB,2)
    }
}

function Invoke-HealthChecks {
    param([Parameter(Mandatory)][hashtable]$Config)

    [pscustomobject]@{
        Backend = Test-HttpEndpoint -Url $Config.BACKEND_HEALTH_URL
        Frontend = Test-HttpEndpoint -Url $Config.FRONTEND_HEALTH_URL
        BackendPort = Test-TcpPort -Host "127.0.0.1" -Port 5000
        Disk = Test-DiskSpace
        Timestamp = Get-Date
    }
}

Export-ModuleMember -Function Test-HttpEndpoint,Test-TcpPort,Test-DiskSpace,Invoke-HealthChecks
