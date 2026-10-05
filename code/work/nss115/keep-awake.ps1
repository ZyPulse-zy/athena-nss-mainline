$ErrorActionPreference='Stop'
$deadline=[DateTimeOffset]::Parse('2026-10-06T10:00:00+08:00')
if([DateTimeOffset]::Now -ge $deadline){exit 0}
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class AthenaNightAwake {
 [DllImport("kernel32.dll", SetLastError=true)]
 public static extern uint SetThreadExecutionState(uint flags);
}
'@
try {
 if([AthenaNightAwake]::SetThreadExecutionState([uint32]2147483649) -eq 0){throw 'Temporary system-awake request failed'}
 while([DateTimeOffset]::Now -lt $deadline){Start-Sleep -Seconds 20}
} finally {
 [void][AthenaNightAwake]::SetThreadExecutionState([uint32]2147483648)
}
