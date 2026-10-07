param([Parameter(Mandatory=$true)][string]$PlanPath)
$ErrorActionPreference='Stop'
$taskPlan=Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json
$taskDir=Split-Path -Parent $PlanPath
if($taskPlan.seconds -ne 180 -or $taskPlan.owner -notmatch '^[a-f0-9]{32}$' -or -not $taskPlan.cs2LaunchedByThisSession){throw 'Unexpected client bounds'}
function Read-ExactProcess($identity){
 $taskProcess=Get-Process -Id $identity.pid -ErrorAction SilentlyContinue
 if(-not $taskProcess){return $null}
 if($taskProcess.Path -ne $identity.path -or $taskProcess.StartTime.ToUniversalTime().ToString('o') -ne $identity.startedAt){throw 'Application identity changed'}
 return $taskProcess
}
if(-not(Read-ExactProcess $taskPlan.steam) -or -not(Read-ExactProcess $taskPlan.cs2)){throw 'Bound application absent before guard'}
$taskClock=[Diagnostics.Stopwatch]::StartNew()
while($taskClock.Elapsed.TotalSeconds -lt $taskPlan.seconds){
 $taskCancel=Join-Path $taskDir 'cancel'
 if((Test-Path -LiteralPath $taskCancel) -and (Get-Content -LiteralPath $taskCancel -Raw) -eq $taskPlan.owner){
  @{passed=$true;cancelledAfterClientRestore=$true;timedExitExecuted=$false;observedAt=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskDir 'result.json') -Encoding utf8
  exit 0
 }
 @{ready=$true;pid=$PID;elapsedSeconds=$taskClock.Elapsed.TotalSeconds;deadlineSeconds=180;exactApplicationsOnly=$true;at=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskDir 'heartbeat-private.json') -Encoding utf8
 Start-Sleep -Milliseconds 500
}
$taskGame=Read-ExactProcess $taskPlan.cs2
if($taskGame){Stop-Process -Id $taskGame.Id -Force}
$taskSteam=Read-ExactProcess $taskPlan.steam
if($taskSteam){Start-Process -FilePath $taskPlan.steam.path -ArgumentList '-shutdown' -WindowStyle Hidden | Out-Null}
$taskFinish=[Diagnostics.Stopwatch]::StartNew()
while($taskFinish.Elapsed.TotalSeconds -lt 20 -and (Read-ExactProcess $taskPlan.steam)){Start-Sleep -Milliseconds 500}
$taskGone=(-not(Read-ExactProcess $taskPlan.cs2)) -and (-not(Read-ExactProcess $taskPlan.steam))
@{passed=$taskGone;timedExitExecuted=$true;exactApplicationsOnly=$true;deadlineSeconds=180;originalClientUiRestored=$false;observedAt=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskDir 'result.json') -Encoding utf8
if(-not $taskGone){throw 'Bound application shutdown not verified'}
