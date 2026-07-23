<#
===============================================================================
SIRMS Deployment Toolkit
Module : Report.psm1
Purpose: Deployment Report Generation
Version: 1.0
===============================================================================
#>

Set-StrictMode -Version Latest

function New-DeploymentReport {
    param(
        [Parameter(Mandatory)][hashtable]$Context,
        [Parameter(Mandatory)][string]$ReportDirectory
    )

    if(-not (Test-Path $ReportDirectory)){
        New-Item -ItemType Directory -Path $ReportDirectory -Force | Out-Null
    }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

    $jsonFile = Join-Path $ReportDirectory "deployment_$timestamp.json"
    $htmlFile = Join-Path $ReportDirectory "deployment_$timestamp.html"

    $Context | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $jsonFile

    $html = @"
<html>
<head>
<title>SIRMS Deployment Report</title>
<style>
body{font-family:Segoe UI,Arial;margin:20px;}
table{border-collapse:collapse;width:100%;}
th,td{border:1px solid #ccc;padding:8px;text-align:left;}
th{background:#efefef;}
</style>
</head>
<body>
<h2>SIRMS Deployment Report</h2>
<table>
<tr><th>Property</th><th>Value</th></tr>
"@

    foreach($p in $Context.GetEnumerator()){
        $value = if($p.Value -is [System.Collections.IEnumerable] -and
                     $p.Value -isnot [string]){
            ($p.Value | ConvertTo-Json -Compress)
        } else {
            "$($p.Value)"
        }

        $html += "<tr><td>$($p.Key)</td><td>$value</td></tr>`n"
    }

    $html += @"
</table>
</body>
</html>
"@

    Set-Content -Path $htmlFile -Value $html -Encoding UTF8

    [pscustomobject]@{
        JsonReport = $jsonFile
        HtmlReport = $htmlFile
    }
}

function Show-DeploymentReport {
    param([Parameter(Mandatory)]$Context)

    Write-Host ""
    Write-Host "================ Deployment Summary ================"
    foreach($item in $Context.GetEnumerator()){
        Write-Host ("{0,-20}: {1}" -f $item.Key,$item.Value)
    }
    Write-Host "===================================================="
}

Export-ModuleMember -Function `
New-DeploymentReport,`
Show-DeploymentReport
