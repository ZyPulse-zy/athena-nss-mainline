$ErrorActionPreference='Stop'
$taskRoot='work/v55-run-20261007125958-d0f31511'
if(Test-Path -LiteralPath (Join-Path $taskRoot 'load-latest-private.json')){throw 'Full client requires the original guard closure'}
$taskSetup=Get-Content -LiteralPath (Join-Path $taskRoot 'endpoint-setup-private.json') -Raw | ConvertFrom-Json
foreach($taskFile in @('client-binding-private.json','launch-receipt.json','status-private.json','client-launch-private.json')){
 if(Test-Path -LiteralPath (Join-Path $taskSetup.dir $taskFile)){throw 'Client launch began; absence cannot replace the independent client guard proof'}
}
$taskClosure=Get-Content -LiteralPath (Join-Path $taskRoot 'closure-pointer.json') -Raw | ConvertFrom-Json
$taskPattern=[regex]::Escape($taskRoot.Replace('/','\')).Replace('\\','[\\/]')
$taskOwned=@(Get-CimInstance Win32_Process | Where-Object {$_.ProcessId -ne $PID -and $_.CommandLine -match $taskPattern -and $_.CommandLine -match '(native-client\.mjs|client-watchdog\.ps1|pilot-supervisor\.mjs|udp-probe\.(mjs|py))'})
$taskOwned | Select-Object Name,ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskClosure.directory 'owned-process-inventory-private.json') -Encoding utf8
if($taskOwned.Count -ne 0){throw 'Owned probe or fixture process remains'}
$taskReceipt=@{passed=$true;observedAt=[DateTime]::UtcNow.ToString('o');readonly=$true;ownedTestProcessesRemaining=0;clientNeverLaunched=$true;guardProofNotSubstituted=$true;clientDeadlineReset=$false}
$taskReceipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskClosure.directory 'client-closure.json') -Encoding utf8
$taskReceipt | ConvertTo-Json -Depth 8 -Compress
