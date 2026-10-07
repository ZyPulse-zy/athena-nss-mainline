$ErrorActionPreference='Stop'
$taskRoot=Join-Path (Get-Location) 'work/v34-normal'
$taskClosure=Get-Content -LiteralPath (Join-Path $taskRoot 'closure-pointer.json') -Raw | ConvertFrom-Json
$taskPointer=Get-Content -LiteralPath (Join-Path $taskRoot 'application-current-private.json') -Raw | ConvertFrom-Json
foreach($taskName in @('plan-private.json','guard-ready.json','heartbeat-private.json','result.json','watchdog-source-private.ps1')){Copy-Item -LiteralPath (Join-Path $taskPointer.directory $taskName) -Destination (Join-Path $taskClosure.directory $taskName) -ErrorAction Stop}
$taskResult=Get-Content -LiteralPath (Join-Path $taskClosure.directory 'result.json') -Raw | ConvertFrom-Json
$taskReady=Get-Content -LiteralPath (Join-Path $taskClosure.directory 'guard-ready.json') -Raw | ConvertFrom-Json
if(-not $taskResult.passed -or -not $taskReady.readyBeforeDownload -or $taskReady.deadlineSeconds -ne 180){throw 'Client guard closure unproved'}
if(Get-Process -Id $taskPointer.guardPid -ErrorAction SilentlyContinue){throw 'Original guard remains'}
$taskProcesses=@(Get-CimInstance Win32_Process | Where-Object {$_.ProcessId -ne $PID -and $_.CommandLine -match '(?i)work[\\/]v34-normal|application-watchdog\.ps1|steam\.exe|cs2\.exe'} | Select-Object Name,ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine)
$taskProcesses | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskClosure.directory 'process-inventory-private.json') -Encoding utf8
$taskOwned=@($taskProcesses | Where-Object {$_.Name -match '^(node|powershell|pwsh)\.exe$' -and $_.CommandLine -match '(?i)(application-watchdog\.ps1|run-session\.mjs|[/\\]session\.mjs)'})
$taskGames=@(Get-Process cs2 -ErrorAction SilentlyContinue)
if($taskOwned.Count -ne 0 -or $taskGames.Count -ne 0){throw 'Owned controller, guard or CS2 remains'}
$taskReceipt=@{passed=$true;observedAt=[DateTime]::UtcNow.ToString('o');readonly=$true;deadlineSeconds=180;readyBeforeDownload=$true;guardProcessGone=$true;naturalTimedExitPassed=[bool]$taskResult.timedExitExecuted;cancelledAfterClientRestore=[bool]$taskResult.cancelledAfterClientRestore;ownedTestProcessesRemaining=0;cs2ProcessesRemaining=0;steamProcessesRunning=@(Get-Process steam -ErrorAction SilentlyContinue).Count;independentProcessExitDoesNotProveUiRestoration=$true;fullControllerSessionStarted=(Test-Path -LiteralPath (Join-Path $taskRoot 'one-session-attempt.json'));sourceSha256=$taskPointer.sourceSha256}
$taskReceipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskClosure.directory 'client-closure.json') -Encoding utf8
$taskReceipt | ConvertTo-Json -Depth 6 -Compress
