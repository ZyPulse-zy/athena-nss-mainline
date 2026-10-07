$ErrorActionPreference='Stop'
$taskRoot=Join-Path (Get-Location) 'work/v57-run-20261007132452-ab4b5741'
$taskClosure=Get-Content -LiteralPath (Join-Path $taskRoot 'closure-pointer.json') -Raw | ConvertFrom-Json
$taskAll=@(Get-CimInstance Win32_Process | Where-Object {$_.ProcessId -ne $PID})
$taskGuards=@()
$taskOwned=@()
foreach($taskScope in @('work/v57-run-20261007132452-ab4b5741')){
 $taskLoad=Get-Content -LiteralPath (Join-Path $taskScope 'load-latest-private.json') -Raw | ConvertFrom-Json
 $taskBinding=Get-Content -LiteralPath (Join-Path $taskLoad.dir 'client-binding-private.json') -Raw | ConvertFrom-Json
 $taskGuard=Get-Content -LiteralPath $taskBinding.guardResult -Raw | ConvertFrom-Json
 if(-not $taskGuard.passed -or -not $taskGuard.exactClientOnly -or -not $taskGuard.clientExitedBeforeDeadline){throw 'Original independent client closure failed'}
 $taskPattern=[regex]::Escape($taskScope.Replace('/','\')).Replace('\\','[\\/]')
 $taskMatching=@($taskAll | Where-Object {($_.Name -match '^(node|powershell|pwsh)\.exe$' -and $_.CommandLine -match $taskPattern -and $_.CommandLine -match '(native-client\.mjs|client-watchdog\.ps1|pilot-supervisor\.mjs)') -or ($_.Name -eq 'ssh.exe' -and $_.ParentProcessId -eq $taskLoad.clientPid -and $_.CommandLine -match 'python3 -u -c' -and $_.CommandLine -match 'sub2api-dallas')})
 $taskOwned+=$taskMatching
 $taskGuards+=@{scope=$taskScope;passed=[bool]$taskGuard.passed;clientExitedBeforeDeadline=[bool]$taskGuard.clientExitedBeforeDeadline;exactClientOnly=[bool]$taskGuard.exactClientOnly;guardObservedAt=$taskGuard.observedAt;originalClientSeconds=180;independentGuardSeconds=210;ownedProcessesRemaining=$taskMatching.Count}
}
$taskOwned | Select-Object Name,ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskClosure.directory 'owned-process-inventory-private.json') -Encoding utf8
if($taskOwned.Count -ne 0){throw 'Owned fixture, controller, guard or sender remains'}
$taskReceipt=@{passed=$true;observedAt=[DateTime]::UtcNow.ToString('o');readonly=$true;ownedTestProcessesRemaining=0;guards=$taskGuards;cs2ProcessesRemaining=@(Get-Process cs2 -ErrorAction SilentlyContinue).Count;steamProcessesRunning=@(Get-Process steam -ErrorAction SilentlyContinue).Count;cs2Acceptance=$false;steamFactoryAcceptance=$false;clientDeadlineReset=$false}
$taskReceipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskClosure.directory 'client-closure.json') -Encoding utf8
$taskReceipt | ConvertTo-Json -Depth 8 -Compress
