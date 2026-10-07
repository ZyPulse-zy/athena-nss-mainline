$ErrorActionPreference='Stop'
$taskClosure=(Get-Content -LiteralPath 'work/v31-normal/closure-pointer-private.json' -Raw | ConvertFrom-Json).directory
$taskProcesses=@(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -match '(?i)work[\\/]v(30|31)-normal|application-watchdog\.ps1|steam\.exe|cs2\.exe' } | Select-Object Name,ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine)
$taskRaw=Join-Path $taskClosure 'client-process-inventory-v2-private.json'
if(Test-Path -LiteralPath $taskRaw){throw 'Cannot overwrite closure inventory'}
$taskProcesses | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $taskRaw -Encoding utf8
$taskOwn=@($taskProcesses | Where-Object { $_.Name -match '^(node|powershell|pwsh)\.exe$' -and $_.CommandLine -match '(?i)(application-watchdog\.ps1|run-session\.mjs|[/\\]session\.mjs)' })
if($taskOwn.Count -ne 0){throw 'Owned test process remains'}
$taskGuardResults=@()
foreach($taskVersion in @('v30-normal','v31-normal')){
 $taskPointer=Get-Content -LiteralPath ('work/'+$taskVersion+'/application-current-private.json') -Raw | ConvertFrom-Json
 $taskPlan=Get-Content -LiteralPath (Join-Path $taskPointer.directory 'plan-private.json') -Raw | ConvertFrom-Json
 $taskReady=Get-Content -LiteralPath (Join-Path $taskPointer.directory 'guard-ready.json') -Raw | ConvertFrom-Json
 $taskResult=Get-Content -LiteralPath (Join-Path $taskPointer.directory 'result.json') -Raw | ConvertFrom-Json
 if(-not $taskReady.readyBeforeDownload -or $taskPlan.seconds -ne 180 -or -not $taskResult.passed -or -not $taskResult.timedExitExecuted -or -not $taskResult.exactApplicationsOnly){throw 'Independent client exit not proved'}
 if(Get-Process -Id $taskPointer.guardPid -ErrorAction SilentlyContinue){throw 'Original guard PID remains'}
 $taskGuardResults+=@{version=$taskVersion;readyBeforeDownload=$true;deadlineSeconds=180;naturalTimedExitPassed=$true;guardProcessGone=$true;originalClientUiRestoredByGuard=$false;observedAt=$taskResult.observedAt;sourceSha256=$taskPointer.sourceSha256}
}
$taskGameCount=@(Get-Process cs2 -ErrorAction SilentlyContinue).Count
$taskSteamCount=@(Get-Process steam -ErrorAction SilentlyContinue).Count
if($taskGameCount -ne 0){throw 'CS2 remains after independent deadline'}
$taskReceipt=@{
 passed=$true;readonly=$true;observedAt=[DateTime]::UtcNow.ToString('o');ownedTestProcessesRemaining=0;cs2ProcessesRemaining=$taskGameCount;steamProcessesRemaining=$taskSteamCount;guards=$taskGuardResults;
 independentProcessExitDoesNotProveOriginalUiRestoration=$true;noNewControllerOrGuardStarted=$true
}
$taskOutput=Join-Path $taskClosure 'client-process-closure.json'
if(Test-Path -LiteralPath $taskOutput){throw 'Cannot overwrite closure result'}
$taskReceipt | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $taskOutput -Encoding utf8
$taskReceipt | ConvertTo-Json -Depth 7 -Compress
