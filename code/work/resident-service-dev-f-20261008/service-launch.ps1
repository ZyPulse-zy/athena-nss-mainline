$ErrorActionPreference='Stop'
$nssWorkspace=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$nssNode='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
$nssScript=Join-Path $PSScriptRoot 'daemon.mjs'
$nssToken=[guid]::NewGuid().ToString('n')
$nssOut=Join-Path $PSScriptRoot ('launch-'+$nssToken+'-stdout-private.log')
$nssErr=Join-Path $PSScriptRoot ('launch-'+$nssToken+'-stderr-private.log')
$nssChild=Start-Process -FilePath $nssNode -ArgumentList @(('"'+$nssScript+'"'),'run') -WorkingDirectory $nssWorkspace -WindowStyle Hidden -RedirectStandardOutput $nssOut -RedirectStandardError $nssErr -PassThru
$nssLaunch=@{startedAt=(Get-Date).ToUniversalTime().ToString('o');pid=$nssChild.Id;stdout=$nssOut;stderr=$nssErr;automaticStartAtLogon=$false}
$nssTemp=Join-Path $PSScriptRoot ('launch-'+$nssToken+'-receipt.tmp')
[IO.File]::WriteAllText($nssTemp,($nssLaunch|ConvertTo-Json -Depth 4),(New-Object Text.UTF8Encoding($false)))
Move-Item -LiteralPath $nssTemp -Destination (Join-Path $PSScriptRoot 'launch-latest-private.json') -Force
$nssChild.WaitForExit()
$nssChild.Refresh()
$nssExit=$nssChild.ExitCode
if($null -eq $nssExit){throw 'Child exit status unavailable; refusing to report success'}
exit ([int]$nssExit)
