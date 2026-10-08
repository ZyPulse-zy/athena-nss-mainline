param([ValidateSet('Inspect','Install','Start','Status','Stop','Uninstall')][string]$Mode='Inspect')
$ErrorActionPreference='Stop'
$nssWorkspace=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$nssNode='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
$nssDaemon=Join-Path $PSScriptRoot 'daemon.mjs'
$nssName='Athena-NSS-Controller-Manual'
$nssLauncher=Join-Path $PSScriptRoot 'service-launch.ps1'
$nssPowerShell=Join-Path $env:SystemRoot 'System32/WindowsPowerShell/v1.0/powershell.exe'
$nssArguments='-NoProfile -NonInteractive -WindowStyle Hidden -File "'+$nssLauncher+'"'
Set-Location -LiteralPath $nssWorkspace
function Assert-NssTaskOwner($nssTask){
 if($nssTask.Actions.Count -ne 1 -or $nssTask.Actions[0].Execute -ne $nssPowerShell -or $nssTask.Actions[0].Arguments -ne $nssArguments -or $nssTask.Actions[0].WorkingDirectory -ne $nssWorkspace){throw 'Existing named task belongs to another action; refusing to modify it'}
}
if($Mode -eq 'Inspect'){& $nssNode $nssDaemon inspect;exit $LASTEXITCODE}
if($Mode -eq 'Install'){
 & $nssNode $nssDaemon inspect
 if($LASTEXITCODE -ne 0){throw 'Local qualification refused before task installation'}
 $nssExisting=Get-ScheduledTask -TaskName $nssName -TaskPath '\' -ErrorAction SilentlyContinue
 if($nssExisting){Assert-NssTaskOwner $nssExisting;@{installed=$true;alreadyPresent=$true;automaticStartAtLogon=$false}|ConvertTo-Json -Compress;exit 0}
 $nssAction=New-ScheduledTaskAction -Execute $nssPowerShell -Argument $nssArguments -WorkingDirectory $nssWorkspace
 $nssPrincipal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
 $nssSettings=New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -DisallowHardTerminate
 $nssTask=New-ScheduledTask -Action $nssAction -Principal $nssPrincipal -Settings $nssSettings -Description 'Athena NSS manual resident pilot; finite 90-second generations, no traffic creation, no logon trigger, no failure restart.'
 Register-ScheduledTask -TaskName $nssName -TaskPath '\' -InputObject $nssTask | Out-Null
 $nssTask=Get-ScheduledTask -TaskName $nssName -TaskPath '\';Assert-NssTaskOwner $nssTask
 if($nssTask.Triggers.Count -gt 0 -or $nssTask.Settings.RestartCount -gt 0){throw 'Unexpected automatic trigger or restart'}
 @{installed=$true;automaticStartAtLogon=$false;automaticRestartOnFailure=$false;existingTasksUnchanged=$true}|ConvertTo-Json -Compress;exit 0
}
if($Mode -eq 'Stop'){& $nssNode $nssDaemon stop;exit $LASTEXITCODE}
$nssTask=Get-ScheduledTask -TaskName $nssName -TaskPath '\' -ErrorAction Stop;Assert-NssTaskOwner $nssTask
if($Mode -eq 'Start'){Start-ScheduledTask -TaskName $nssName -TaskPath '\';@{startRequested=$true;task=$nssName;automaticStartAtLogon=$false}|ConvertTo-Json -Compress;exit 0}
if($Mode -eq 'Status'){& $nssNode $nssDaemon status;if($LASTEXITCODE -ne 0){exit $LASTEXITCODE};Get-ScheduledTaskInfo -TaskName $nssName -TaskPath '\'|Select-Object LastTaskResult,LastRunTime|ConvertTo-Json -Compress;exit 0}
if($Mode -eq 'Uninstall'){
 if($nssTask.State -eq 'Running'){throw 'Request graceful Stop and confirm restoration before uninstall'}
 if(Test-Path -LiteralPath 'work/resident-dev-20261007/active-lock'){throw 'Generation restoration unconfirmed; retain task definition'}
 if(Test-Path -LiteralPath 'work/resident-dev-20261007/controller-lock'){throw 'Controller still owns its lock'}
 Unregister-ScheduledTask -TaskName $nssName -TaskPath '\' -Confirm:$false
 @{uninstalled=$true;routerWrites=$false;unrelatedTasksUnchanged=$true}|ConvertTo-Json -Compress
}
