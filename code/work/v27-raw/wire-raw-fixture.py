"""Wire the existing finite endpoint/guard to the owned raw fixture."""
from pathlib import Path
r=Path(__file__).resolve().parent
def change(name,old,new):
    p=r/name;b=p.read_bytes();a=old.encode();assert b.count(a)==1,(name,old);p.write_bytes(b.replace(a,new.encode()))
change('start-dallas.mjs',"root+'/server.py'","root+'/raw-server.py'")
change('close-endpoint.mjs',"work/v27-raw/server.py","work/v27-raw/raw-server.py")
change('start-dallas.mjs',"config.tcpPort=22;config.tcpSourcePort=0;","config.tcpPort=45817;config.tcpSourcePort=0;const portBase=57000+crypto.randomInt(1000);config.tcpSourcePorts=Object.fromEntries(['tcp','tcp2','tcp3','tcp4'].map((slot,i)=>[slot,portBase+i*200]));")
change('start-dallas.mjs',"root+'/native-client.mjs'","root+'/raw-client.mjs'")
change('start-dallas.mjs',"bulkTransport:'owned native OpenSSH download'","bulkTransport:'owned nonce-authenticated raw TCP download'")
change('owned-load-policy.mjs',"'client-observed stdout download bytes'","'client-observed raw payload bytes'")
change('owned-load-policy.mjs',"config.tcpPort,22","config.tcpPort,45817")
change('owned-load-policy.mjs',"'owned native OpenSSH download'","'owned nonce-authenticated raw TCP download'")
change('read-controlled.mjs',"status.bulkTransport,'owned native OpenSSH download'","status.bulkTransport,'owned nonce-authenticated raw TCP download'")
change('read-controlled.mjs',"status.tcpPort,22","status.tcpPort,45817")
change('read-controlled.mjs',"e.RemotePort===22","e.RemotePort===45817")
p=r/'read-controlled.mjs';b=p.read_bytes();start=b.index(b'const ps=`');end=b.index(b'`;\r\nconst pcRaw',start)
ps=r'''const ps=`$ErrorActionPreference='Stop';$b=Get-Content -LiteralPath '${binding.configPath.replaceAll("'","''").replace(/client-config-private.json$/,'client-binding-private.json')}' -Raw|ConvertFrom-Json;$p=Get-Process -Id $b.clientPid -ErrorAction Stop;if($p.StartTime.ToUniversalTime().Ticks -ne [datetime]::Parse($b.clientStart).ToUniversalTime().Ticks -or $p.Path -ne $b.clientExe){throw 'Controlled client instance changed'};$k=Get-CimInstance Win32_Process -Filter ('ProcessId='+$p.Id);if($k.ExecutablePath -ne $b.clientExe -or -not $k.CommandLine.Contains($b.scriptPath) -or -not $k.CommandLine.Contains($b.configPath)){throw 'Owned raw client arguments changed'};$s=Get-Content -LiteralPath '${binding.configPath.replaceAll("'","''").replace(/client-config-private.json$/,'status-private.json')}' -Raw|ConvertFrom-Json;if(@($s.tcpChildren).Count -ne 4 -or @($s.tcpChildren.sourcePort|Select-Object -Unique).Count -ne 4){throw 'Four exact owned raw ports required'};$tcp=@(Get-NetTCPConnection -OwningProcess $p.Id -State Established -ErrorAction SilentlyContinue);$rows=@();foreach($v in $s.tcpChildren){if($v.ownerPid -ne $p.Id -or $v.executable -ne $b.clientExe -or -not $v.connected){throw 'Owned raw slot changed'};$matches=@($tcp|Where-Object{$_.LocalPort -eq [int]$v.sourcePort -and $_.RemotePort -eq 45817 -and $_.RemoteAddress -eq '172.93.163.251' -and $_.LocalAddress -eq '192.168.237.207'});if($matches.Count -ne 1){throw 'Owned raw socket absent or ambiguous'};foreach($e in $matches){$rows+=@{LocalAddress=$e.LocalAddress;LocalPort=$e.LocalPort;RemoteAddress=$e.RemoteAddress;RemotePort=$e.RemotePort;slot=$v.slot}}};@{pid=$p.Id;tcp=@($rows);udp=@(Get-NetUDPEndpoint -OwningProcess $p.Id -ErrorAction SilentlyContinue|Select-Object LocalAddress,LocalPort)}|ConvertTo-Json -Depth 5 -Compress'''
p.write_bytes(b[:start]+ps.encode()+b[end:])
old=(r/'wait-four-ssh.mjs').read_bytes().replace(b'fourOwnedSshChildrenReady',b'fourOwnedRawSocketsReady').replace(b'Number.isInteger(x.ownerPid)',b'x.ownerPid===s.pid').replace(b'SSH',b'raw TCP')
(r/'wait-four-raw.mjs').write_bytes(old)
print('Raw fixture wired; no native/Lua/PBR/QoS change')
