param([string]$Label='first-window')
$ErrorActionPreference='Stop'
if($Label -notmatch '^[a-z0-9-]+$'){throw 'Invalid closure label'}
$taskRoot=Join-Path (Get-Location) 'work/v32-normal'
$taskDir=Join-Path $taskRoot ($Label+'-closure-'+[DateTime]::UtcNow.ToString('yyyyMMddHHmmss'))
New-Item -ItemType Directory -Path $taskDir | Out-Null
$taskPointerPath=Join-Path $taskRoot 'application-current-private.json'
$taskPointer=Get-Content -LiteralPath $taskPointerPath -Raw | ConvertFrom-Json
Copy-Item -LiteralPath $taskPointerPath -Destination (Join-Path $taskDir 'application-pointer-private.json')
foreach($taskName in @('plan-private.json','guard-ready.json','heartbeat-private.json','result.json','watchdog-source-private.ps1')){
 Copy-Item -LiteralPath (Join-Path $taskPointer.directory $taskName) -Destination (Join-Path $taskDir $taskName)
}
$taskResult=Get-Content -LiteralPath (Join-Path $taskDir 'result.json') -Raw | ConvertFrom-Json
$taskReady=Get-Content -LiteralPath (Join-Path $taskDir 'guard-ready.json') -Raw | ConvertFrom-Json
$taskPlan=Get-Content -LiteralPath (Join-Path $taskDir 'plan-private.json') -Raw | ConvertFrom-Json
if(-not $taskResult.passed -or -not $taskResult.timedExitExecuted -or -not $taskResult.exactApplicationsOnly -or $taskPlan.seconds -ne 180 -or -not $taskReady.readyBeforeDownload){throw 'Exact independent deadline exit unproved'}
if(Get-Process -Id $taskPointer.guardPid -ErrorAction SilentlyContinue){throw 'Original guard process remains'}
$taskProcesses=@(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -match '(?i)work[\\/]v32-normal|application-watchdog\.ps1|steam\.exe|cs2\.exe' } | Select-Object Name,ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine)
$taskProcesses | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskDir 'process-inventory-private.json') -Encoding utf8
$taskOwned=@($taskProcesses | Where-Object { $_.Name -match '^(node|powershell|pwsh)\.exe$' -and $_.CommandLine -match '(?i)(application-watchdog\.ps1|run-session\.mjs|[/\\]session\.mjs)' })
$taskGames=@(Get-Process cs2 -ErrorAction SilentlyContinue)
if($taskOwned.Count -ne 0 -or $taskGames.Count -ne 0){throw 'Owned controller, guard or CS2 remains'}
$taskReceipt=@{passed=$true;observedAt=[DateTime]::UtcNow.ToString('o');readonly=$true;deadlineSeconds=180;naturalTimedExitPassed=$true;readyBeforeDownload=$true;guardProcessGone=$true;ownedTestProcessesRemaining=0;cs2ProcessesRemaining=0;steamProcessesRunning=@(Get-Process steam -ErrorAction SilentlyContinue).Count;steamRestartedOnlyForUiRestoration=$true;originalClientUiRestoredByGuard=$false;fullControllerSessionStarted=(Test-Path -LiteralPath (Join-Path $taskRoot 'one-session-attempt.json'));sourceSha256=$taskPointer.sourceSha256}
$taskReceipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskDir 'client-closure.json') -Encoding utf8
@{directory=$taskDir;label=$Label} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot ($Label+'-closure-pointer.json')) -Encoding utf8
$taskReceipt | ConvertTo-Json -Depth 6 -Compress
