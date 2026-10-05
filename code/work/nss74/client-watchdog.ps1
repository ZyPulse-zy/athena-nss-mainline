param([Parameter(Mandatory=$true)][string]$PlanPath)
$ErrorActionPreference='Stop'
$plan=Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json
$caseDir=Split-Path -Parent $PlanPath
if($plan.seconds -ne 900 -or $plan.owner -notmatch '^[a-f0-9]{32}$'){throw 'Unexpected watchdog bounds'}
function Read-BoundSteam {
    $p=Get-Process -Id $plan.steamPid -ErrorAction SilentlyContinue
    if(-not $p){return $null}
    try {$p.Refresh();if($p.HasExited){return $null};$currentPath=$p.Path;$currentStart=$p.StartTime.ToUniversalTime().ToString('o')}
    catch {if(-not(Get-Process -Id $plan.steamPid -ErrorAction SilentlyContinue)){return $null};throw}
    if($currentPath -ne $plan.steamPath -or $currentStart -ne $plan.steamStartedAt){
        if(-not(Get-Process -Id $plan.steamPid -ErrorAction SilentlyContinue)){return $null}
        throw 'Steam process identity changed'
    }
    return $p
}
$failure=$null;$bound=$null;$timedExit=$false;$cancelled=$false
try {
    if(-not(Read-BoundSteam)){throw 'Bound Steam instance absent before guard'}
    $watch=[Diagnostics.Stopwatch]::StartNew();$me=Get-Process -Id $PID
    while($watch.Elapsed.TotalSeconds -lt $plan.seconds){
        $cancel=Join-Path $caseDir 'cancel'
        if((Test-Path -LiteralPath $cancel) -and (Get-Content -LiteralPath $cancel -Raw) -eq $plan.owner){$cancelled=$true;break}
        [pscustomobject]@{ready=$true;pid=$PID;startedAt=$me.StartTime.ToUniversalTime().ToString('o');at=[DateTime]::UtcNow.ToString('o');elapsedSeconds=$watch.Elapsed.TotalSeconds;deadlineSeconds=$plan.seconds}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $caseDir 'heartbeat-private.json') -Encoding utf8
        Start-Sleep -Milliseconds 500
    }
    if(-not $cancelled){$bound=Read-BoundSteam;if($bound){Start-Process -FilePath $plan.steamPath -ArgumentList '-shutdown' -WindowStyle Hidden|Out-Null;$timedExit=$true;$ending=[Diagnostics.Stopwatch]::StartNew();while($ending.Elapsed.TotalSeconds -lt 20 -and (Read-BoundSteam)){Start-Sleep -Milliseconds 500}}}
} catch {$failure=$_.Exception.Message}
$gone=-not(Get-Process -Id $plan.steamPid -ErrorAction SilentlyContinue)
$result=[pscustomobject]@{passed=($null -eq $failure -and ($gone -or $cancelled));completedAt=[DateTime]::UtcNow.ToString('o');cancelledAfterClientRestore=$cancelled;timedExitExecuted=$timedExit;exactOriginalSteamInstanceGone=$gone;deadlineSeconds=$plan.seconds;command='steam -shutdown';originalClientUiRestored=$cancelled;failure=$failure}
$result|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $caseDir 'result.json') -Encoding utf8
if(-not $result.passed){throw 'Client watchdog completion failed; receipt saved'}
