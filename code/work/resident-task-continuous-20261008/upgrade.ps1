$ErrorActionPreference='Stop'
$nssWorkspace=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
Set-Location -LiteralPath $nssWorkspace
$nssName='Athena-NSS-Controller-Manual'
$nssOldLauncher=Join-Path $nssWorkspace 'work/resident-service-dev-i-20261008/service-launch.ps1'
$nssNewLauncher=Join-Path $nssWorkspace 'work/resident-continuous-dev-20261008/service-launch.ps1'
$nssOldArgs='-NoProfile -NonInteractive -WindowStyle Hidden -File "'+$nssOldLauncher+'"'
$nssNewArgs='-NoProfile -NonInteractive -WindowStyle Hidden -File "'+$nssNewLauncher+'"'
$nssPowerShell=Join-Path $env:SystemRoot 'System32/WindowsPowerShell/v1.0/powershell.exe'
& 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' 'work/resident-continuous-dev-20261008/daemon.mjs' inspect
if($LASTEXITCODE -ne 0){throw 'Qualification refused before task action update'}
foreach($nssLock in @('work/resident-dev-20261007/active-lock','work/resident-dev-20261007/controller-lock')){if(Test-Path -LiteralPath $nssLock){throw 'Owned process or unconfirmed generation remains'}}
$nssTask=Get-ScheduledTask -TaskName $nssName -TaskPath '\'
if($nssTask.State -eq 'Running'){throw 'Original task still running'}
if($nssTask.Actions.Count -ne 1 -or $nssTask.Actions[0].Execute -ne $nssPowerShell -or $nssTask.Actions[0].Arguments -ne $nssOldArgs -or $nssTask.Actions[0].WorkingDirectory -ne $nssWorkspace){throw 'Unexpected current task owner/action'}
$nssOtherTasks=@{}
foreach($nssOther in @(Get-ScheduledTask | Where-Object {$_.TaskName -ne $nssName -and $_.TaskName -match 'Athena|Codex.*(NSS|Keep)'})){$nssKey=$nssOther.TaskPath+$nssOther.TaskName;$nssOtherTasks[$nssKey]=Export-ScheduledTask -TaskName $nssOther.TaskName -TaskPath $nssOther.TaskPath}
$nssBefore=Export-ScheduledTask -TaskName $nssName -TaskPath '\'
$nssBackup=Join-Path $PSScriptRoot 'continuous-scheduled-task-before-private.xml'
if(Test-Path -LiteralPath $nssBackup){throw 'Existing task upgrade receipt must be preserved'}
[IO.File]::WriteAllText($nssBackup,$nssBefore,[Text.UTF8Encoding]::new($false))
[xml]$nssXml=$nssBefore
$nssNs=New-Object Xml.XmlNamespaceManager($nssXml.NameTable)
$nssNs.AddNamespace('t',$nssXml.DocumentElement.NamespaceURI)
$nssArgNode=$nssXml.SelectSingleNode('/t:Task/t:Actions/t:Exec/t:Arguments',$nssNs)
if($nssArgNode.InnerText -ne $nssOldArgs){throw 'Original exact launch arguments differ'}
$nssArgNode.InnerText=$nssNewArgs
$nssExpected=$nssXml.OuterXml
Register-ScheduledTask -TaskName $nssName -TaskPath '\' -Xml $nssExpected -Force | Out-Null
[xml]$nssAfter=Export-ScheduledTask -TaskName $nssName -TaskPath '\'
$nssNsAfter=New-Object Xml.XmlNamespaceManager($nssAfter.NameTable)
$nssNsAfter.AddNamespace('t',$nssAfter.DocumentElement.NamespaceURI)
$nssAfterArgs=$nssAfter.SelectSingleNode('/t:Task/t:Actions/t:Exec/t:Arguments',$nssNsAfter)
if($nssAfterArgs.InnerText -ne $nssNewArgs){throw 'New exact launch arguments not installed'}
foreach($nssSection in @('Settings','Principals','Triggers','Actions')){
 $nssLeft=$nssXml.SelectSingleNode('/t:Task/t:'+$nssSection,$nssNs).OuterXml
 $nssRight=$nssAfter.SelectSingleNode('/t:Task/t:'+$nssSection,$nssNsAfter).OuterXml
 if($nssLeft -ne $nssRight){throw ('Unexpected task section drift: '+$nssSection)}
}
foreach($nssKey in $nssOtherTasks.Keys){$nssOther=Get-ScheduledTask|Where-Object {($_.TaskPath+$_.TaskName) -eq $nssKey};if((Export-ScheduledTask -TaskName $nssOther.TaskName -TaskPath $nssOther.TaskPath) -ne $nssOtherTasks[$nssKey]){throw 'Unrelated Athena/Codex task changed'}}
$nssTask=Get-ScheduledTask -TaskName $nssName -TaskPath '\'
if($nssTask.Triggers.Count -gt 0 -or $nssTask.Settings.RestartCount -gt 0 -or $nssTask.Settings.AllowHardTerminate){throw 'Unexpected auto restart or force-termination policy'}
$nssReceipt=@{passed=$true;at=(Get-Date).ToUniversalTime().ToString('o');onlyOwnedLaunchArgumentsChanged=$true;otherRelatedTasksUnchanged=$true;otherTasks=$nssOtherTasks.Count;noLogonTrigger=$true;noFailureRestart=$true;noForceTermination=$true;routerWrites=$false;oldCandidatePreserved=$true}
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'continuous-task-upgrade-private.json'),($nssReceipt|ConvertTo-Json -Depth 4),[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'continuous-scheduled-task-after-private.xml'),$nssAfter.OuterXml,[Text.UTF8Encoding]::new($false))
$nssReceipt|ConvertTo-Json -Compress
Start-ScheduledTask -TaskName $nssName -TaskPath '\'
@{startRequested=$true;task=$nssName;candidate='continuous';automaticLogonStart=$false}|ConvertTo-Json -Compress

