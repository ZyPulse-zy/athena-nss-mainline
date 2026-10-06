param([ValidateSet('start','stop','status')][string]$Action='status')
$ErrorActionPreference='Stop'
$workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$taskNode = 'C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
if (-not (Test-Path -LiteralPath $taskNode)) { throw 'Configured Node runtime is unavailable' }
Push-Location -LiteralPath $workspace
try {
  & $taskNode 'work/v11/service.mjs' $Action
  if ($LASTEXITCODE -ne 0) { throw 'Athena command failed; original local evidence is preserved' }
} finally { Pop-Location }
