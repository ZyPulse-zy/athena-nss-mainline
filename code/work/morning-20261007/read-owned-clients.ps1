$ErrorActionPreference='Stop'
$taskRoot='C:\Users\lishu\Documents\Codex\2026-09-30\referenced-chatgpt-conversation-this-is-an-2\work\'
$taskFolders=@('v12','v13-two','v14-duration','v15-qos','v16-three','v17-cap','v18-borrow','v19-borrow','v20-five','v21-fiveflow','v22-fiveflow','v23-fiveflow','v24-fiveflow','v25-normal','v26-normal','v27-raw')
$taskNames=@('native-client.mjs','native-client-v5.mjs','download-client.mjs','raw-client.mjs','pilot-supervisor.mjs','client-watchdog.ps1')
$taskRows=@(Get-CimInstance Win32_Process -Filter "Name='node.exe' OR Name='ssh.exe' OR Name='powershell.exe' OR Name='python.exe'")
$taskOwned=@($taskRows|Where-Object {
 $taskCommand=[string]$_.CommandLine
 $taskLiteral=$taskCommand.Replace('/','\').ToLowerInvariant()
 $taskFolderMatch=@($taskFolders|Where-Object {$taskLiteral.Contains(($taskRoot+$_+'\').ToLowerInvariant())}).Count -gt 0
 $taskNameMatch=@($taskNames|Where-Object {$taskLiteral.Contains($_)}).Count -gt 0
 ($taskFolderMatch -and $taskNameMatch) -or ($_.Name -eq 'ssh.exe' -and $taskCommand.Contains('sub2api-dallas') -and $taskCommand.Contains('Finite RAM-only sender over the existing authenticated SSH session'))
})
@{passed=($taskOwned.Count -eq 0);readonly=$true;knownNightFixtureNamespacesChecked=$taskFolders.Count;ownedClientControllerGuardOrSenderProcessesRemaining=$taskOwned.Count;observedAt=(Get-Date).ToUniversalTime().ToString('o')}|ConvertTo-Json -Compress
if($taskOwned.Count -ne 0){exit 1}
