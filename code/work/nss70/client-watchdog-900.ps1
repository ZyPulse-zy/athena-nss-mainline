param([Parameter(Mandatory=$true)][string]$PlanPath)
$ErrorActionPreference = 'Stop'
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json
$caseDir = Split-Path -Parent $PlanPath
if ($plan.seconds -ne 900 -or $plan.owner -notmatch '^[a-f0-9]{32}$') { throw 'Unexpected watchdog bounds' }
function Read-BoundSteam {
    $p = Get-Process -Id $plan.steamPid -ErrorAction SilentlyContinue
    if (-not $p) { return $null }
    if ($p.Path -ne $plan.steamPath -or $p.StartTime.ToUniversalTime().ToString('o') -ne $plan.steamStartedAt) {
        throw 'Steam process identity changed'
    }
    return $p
}
if (-not (Read-BoundSteam)) { throw 'Bound Steam instance absent before guard' }
$watch = [System.Diagnostics.Stopwatch]::StartNew()
$me = Get-Process -Id $PID
$cancelPath = Join-Path $caseDir 'cancel'
$heartbeatPath = Join-Path $caseDir 'heartbeat-private.json'
while ($watch.Elapsed.TotalSeconds -lt $plan.seconds) {
    if (Test-Path -LiteralPath $cancelPath) {
        if ((Get-Content -LiteralPath $cancelPath -Raw) -eq $plan.owner) {
            [pscustomobject]@{ passed=$true; completedAt=[DateTime]::UtcNow.ToString('o'); cancelledAfterClientRestore=$true; timedExitExecuted=$false } |
                ConvertTo-Json | Set-Content -LiteralPath (Join-Path $caseDir 'result.json') -Encoding utf8
            exit 0
        }
    }
    [pscustomobject]@{ ready=$true; pid=$PID; startedAt=$me.StartTime.ToUniversalTime().ToString('o'); at=[DateTime]::UtcNow.ToString('o'); elapsedSeconds=$watch.Elapsed.TotalSeconds; deadlineSeconds=$plan.seconds } |
        ConvertTo-Json | Set-Content -LiteralPath $heartbeatPath -Encoding utf8
    Start-Sleep -Milliseconds 500
}
$bound = Read-BoundSteam
if ($bound) {
    Start-Process -FilePath $plan.steamPath -ArgumentList '-shutdown' -WindowStyle Hidden | Out-Null
    $endWatch = [System.Diagnostics.Stopwatch]::StartNew()
    while ($endWatch.Elapsed.TotalSeconds -lt 20 -and (Read-BoundSteam)) { Start-Sleep -Milliseconds 500 }
}
$gone = -not (Read-BoundSteam)
[pscustomobject]@{ passed=$gone; completedAt=[DateTime]::UtcNow.ToString('o'); timedExitExecuted=($null -ne $bound); exactOriginalSteamInstanceGone=$gone; deadlineSeconds=$plan.seconds; command='steam -shutdown'; originalClientUiRestored=$false } |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $caseDir 'result.json') -Encoding utf8
if (-not $gone) { throw 'Timed graceful Steam exit was not verified' }

