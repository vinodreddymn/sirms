<#
SIRMS Deployment Toolkit - SSH.psm1 v2.0
#>
Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"
function Invoke-SSHProcess{
param([string]$Executable,[string[]]$Arguments,[int]$Retries=1)
for($i=1;$i-le $Retries;$i++){
$o=& $Executable @Arguments 2>&1;$c=$LASTEXITCODE
if($c-eq 0){return $o}
if($i-lt $Retries){Start-Sleep 2}}
throw "$Executable failed (exit code $c)`n$($o-join [Environment]::NewLine)"}
function Invoke-SshCommand{
param([string]$Host,[string]$User,[string]$KeyFile,[string]$Command,[int]$Port=22,[int]$Retries=1)
$args=@("-i",$KeyFile,"-p",$Port,"-o","StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","$User@$Host","bash","-lc",$Command)
Invoke-SSHProcess -Executable ssh -Arguments $args -Retries $Retries}
function Ensure-RemoteDirectory{
param([string]$Host,[string]$User,[string]$KeyFile,[string]$Directory,[int]$Port=22)
Invoke-SshCommand -Host $Host -User $User -KeyFile $KeyFile -Port $Port -Command ("mkdir -p '{0}'"-f $Directory)|Out-Null}
function Copy-FileToRemote{
param([string]$LocalFile,[string]$RemotePath,[string]$Host,[string]$User,[string]$KeyFile,[int]$Port=22)
if(!(Test-Path $LocalFile)){throw "Local file not found: $LocalFile"}
Ensure-RemoteDirectory -Host $Host -User $User -KeyFile $KeyFile -Directory $RemotePath -Port $Port
$args=@("-i",$KeyFile,"-P",$Port,"-o","StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null",$LocalFile,"$User@$Host`:$RemotePath/")
Invoke-SSHProcess -Executable scp -Arguments $args|Out-Null}
function Copy-FileFromRemote{
param([string]$RemoteFile,[string]$LocalPath,[string]$Host,[string]$User,[string]$KeyFile,[int]$Port=22)
$args=@("-i",$KeyFile,"-P",$Port,"-o","StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","$User@$Host`:$RemoteFile",$LocalPath)
Invoke-SSHProcess -Executable scp -Arguments $args|Out-Null}
function Test-SshConnection{
param([string]$Host,[string]$User,[string]$KeyFile,[int]$Port=22)
try{Invoke-SshCommand -Host $Host -User $User -KeyFile $KeyFile -Port $Port -Command "echo connected"|Out-Null;$true}catch{$false}}
Export-ModuleMember -Function Invoke-SshCommand,Copy-FileToRemote,Copy-FileFromRemote,Ensure-RemoteDirectory,Test-SshConnection
