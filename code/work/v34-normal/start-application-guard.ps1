param([Parameter(Mandatory=$true)][string]$DownloadDescription)
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path -LiteralPath 'work/v34-normal').Path
$taskSteam=@(Get-Process -Name steam -ErrorAction Stop)
$taskGame=@(Get-Process -Name cs2 -ErrorAction Stop)
if($taskSteam.Count -ne 1 -or $taskGame.Count -ne 1){throw 'Application instance not unique'}
if($taskSteam[0].Path -ne 'C:\Program Files (x86)\Steam\steam.exe' -or $taskGame[0].Path -ne 'D:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\game\bin\win64\cs2.exe'){throw 'Unexpected application path'}
$taskDir=Join-Path $taskRoot ('application-'+[DateTime]::UtcNow.ToString('yyyyMMddHHmmss')+'-'+[Guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Path $taskDir -ErrorAction Stop | Out-Null
function Identity($process){return @{pid=$process.Id;path=$process.Path;startedAt=$process.StartTime.ToUniversalTime().ToString('o')}}
$taskPlan=@{seconds=180;owner=[Guid]::NewGuid().ToString('N');steam=(Identity $taskSteam[0]);cs2=(Identity $taskGame[0]);cs2LaunchedByThisSession=$true;beforeCs2Running=$false;beforeDownloadPaused=$true;beforeLimitChanged=$false;temporarySteamLimitMbps=32;originalSteamLimitEnabled=$false;download=$DownloadDescription;observedAt=[DateTime]::UtcNow.ToString('o')}
$taskPlanPath=Join-Path $taskDir 'plan-private.json'
$taskPlan | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $taskPlanPath -Encoding utf8
$taskSource=Join-Path $taskRoot 'application-watchdog.ps1'
$taskHash=(Get-FileHash -LiteralPath $taskSource -Algorithm SHA256).Hash.ToLowerInvariant()
Copy-Item -LiteralPath $taskSource -Destination (Join-Path $taskDir 'watchdog-source-private.ps1') -ErrorAction Stop
$taskGuard=Start-Process -FilePath powershell.exe -ArgumentList @('-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',$taskSource,'-PlanPath',$taskPlanPath) -WindowStyle Hidden -PassThru
$taskLimit=[Diagnostics.Stopwatch]::StartNew()
$taskHeartbeat=Join-Path $taskDir 'heartbeat-private.json'
while(-not(Test-Path -LiteralPath $taskHeartbeat) -and $taskLimit.Elapsed.TotalSeconds -lt 5){Start-Sleep -Milliseconds 200}
if(-not(Test-Path -LiteralPath $taskHeartbeat)){throw 'Independent application guard not ready'}
$taskReady=Get-Content -LiteralPath $taskHeartbeat -Raw | ConvertFrom-Json
if(-not $taskReady.ready -or $taskReady.pid -ne $taskGuard.Id -or $taskReady.deadlineSeconds -ne 180 -or $taskGuard.HasExited){throw 'Application guard identity not ready'}
@{directory=$taskDir;guardPid=$taskGuard.Id;sourceSha256=$taskHash} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot 'application-current-private.json') -Encoding utf8
@{passed=$true;readyBeforeDownload=$true;deadlineSeconds=180;exactTwoApplicationsOnly=$true;sourceSha256=$taskHash;temporaryClientLimitPlanned=$true;temporarySteamLimitMbps=32;originalSteamLimitEnabled=$false;observedAt=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskDir 'guard-ready.json') -Encoding utf8
@{passed=$true;deadlineSeconds=180;guardReady=$true;exactApplicationsOnly=$true} | ConvertTo-Json -Compress
