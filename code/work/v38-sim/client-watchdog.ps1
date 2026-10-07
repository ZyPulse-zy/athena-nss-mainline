param([string]$BindingPath)
$ErrorActionPreference='Stop'
$taskBinding=Get-Content -LiteralPath $BindingPath -Raw | ConvertFrom-Json
$taskClient=Get-Process -Id $taskBinding.clientPid -ErrorAction Stop
if($taskClient.StartTime.ToUniversalTime().Ticks -ne [datetime]::Parse($taskBinding.clientStart).ToUniversalTime().Ticks){throw 'Client identity changed'}
if($taskClient.Path -ne $taskBinding.clientExe){throw 'Client executable changed'}
$taskExited=$taskClient.WaitForExit(210000)
if(-not $taskExited){
 $taskCurrent=Get-Process -Id $taskBinding.clientPid -ErrorAction SilentlyContinue
 if($taskCurrent -and $taskCurrent.StartTime.ToUniversalTime().Ticks -eq [datetime]::Parse($taskBinding.clientStart).ToUniversalTime().Ticks -and $taskCurrent.Path -eq $taskBinding.clientExe){Stop-Process -Id $taskCurrent.Id -Force}
}
@{passed=$true;clientExitedBeforeDeadline=$taskExited;exactClientOnly=$true;observedAt=(Get-Date).ToUniversalTime().ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $taskBinding.guardResult -Encoding UTF8
